"""main.py - REST API'et (FastAPI). Start: uvicorn main:app --host 0.0.0.0

Hvad er filen?
    Det er "døren" ind til systemet. Alt, hvad Pi'en, Postman og browseren gør,
    sker ved at kalde en af funktionerne herunder over HTTP.

Flowet "event -> beslutning -> handling" sker i POST /measurements:
    1. Event:      Pi'en sender en fugtmåling (Sensor Value Received).
    2. Beslutning: rules.py afgør grøn/gul/rød, og om en alarm skal åbnes eller lukkes.
    3. Handling:   målingen og evt. alarmen gemmes i databasen (Anomaly Detected),
                   og svaret fortæller Pi'en, hvilken farve LED'en skal vise.

Endpoints:
    POST /measurements          modtag en måling fra Pi'en
    GET  /measurements          de seneste målinger (til kontrolcentret)
    GET  /alarms                de seneste alarmer
    POST /alarms/{id}/ack       operatøren kvitterer for en åben alarm
    GET  /                      kontrolcentret (static/index.html)
    GET  /docs                  Swagger: automatisk API-dokumentation fra FastAPI

Hvorfor FastAPI?
    Det laver selv Swagger-dokumentationen (/docs) ud fra koden, og det tjekker
    selv de data, der kommer ind (via Pydantic). Begge dele kræver opgaven.
"""

# --- Imports: værktøjer fra Pythons standardbibliotek -----------------------
from contextlib import asynccontextmanager  # bruges til "lifespan" (kode ved opstart)
from datetime import datetime, timezone  # tidsstempler på målinger og alarmer
from pathlib import Path  # finder static/index.html uanset hvor serveren startes fra

# --- Imports: eksterne pakker (står i requirements.txt) ---------------------
from fastapi import Depends, FastAPI, HTTPException, Query  # web-frameworket
from fastapi.responses import FileResponse  # sender en fil (HTML-siden) som svar
from pydantic import BaseModel, Field  # beskriver og validerer indkommende JSON
from sqlmodel import Session, select  # databasesession og SELECT-forespørgsler

# --- Imports: vores egne filer -----------------------------------------------
import rules  # domænereglerne (grøn/gul/rød, åbn/luk alarm)
from db import Alarm, Measurement, create_tables, get_session  # tabeller og forbindelse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Kører én gang, når serveren starter (før yield) og stopper (efter yield)."""
    create_tables()  # opret tabellerne i databasen, hvis de ikke findes endnu
    yield  # her kører serveren og svarer på forespørgsler


# Selve API-objektet. title og description vises øverst i Swagger (/docs).
app = FastAPI(
    title="Fugt-MVP",
    description="Fugtovervågning for IIS Managed Services: måling -> regel -> alarm.",
    lifespan=lifespan,  # brug funktionen ovenfor ved opstart
)


class MeasurementIn(BaseModel):
    """Det, Pi'en sender. Pydantic afviser selv ugyldige værdier med HTTP 422.

    Eksempel på gyldig JSON: {"device_id": "pi-01", "humidity": 48.2}
    """

    # Hvilken Pi målingen kommer fra. Skal være 1-50 tegn. Mangler den, bruges "pi-01".
    device_id: str = Field(default="pi-01", min_length=1, max_length=50)
    # Selve målingen. ge = "greater or equal", le = "less or equal": kun 0-100 er lovligt,
    # fordi relativ luftfugtighed ikke kan være under 0 eller over 100 %.
    humidity: float = Field(ge=0, le=100, description="Relativ luftfugtighed i %RH")


def now() -> datetime:
    """Tidspunktet lige nu i UTC. UTC, så tiden er ens, uanset hvor serveren står."""
    return datetime.now(timezone.utc)


# --- Endpoint 1: Pi'en sender en måling (hele event-flowet) ------------------
# status_code=201 betyder "Created": en ny måling er oprettet.
@app.post("/measurements", status_code=201)
def receive_measurement(data: MeasurementIn, session: Session = Depends(get_session)):
    # "data" er allerede valideret af MeasurementIn. "session" er databaseforbindelsen,
    # som FastAPI selv henter fra get_session() (det kaldes dependency injection).

    # 1. Event: find farven med reglen, og gem målingen sammen med farven.
    color = rules.status(data.humidity)
    session.add(Measurement(device_id=data.device_id, humidity=data.humidity, status=color, received_at=now()))

    # 2. Beslutning: er der allerede en åben alarm for denne Pi?
    #    "Åben" betyder, at closed_at er tom (None). .first() giver alarmen eller None.
    open_alarm = session.exec(
        select(Alarm).where(Alarm.device_id == data.device_id, Alarm.closed_at == None)  # noqa: E711
    ).first()

    # 3. Handling: åbn en ny alarm eller luk den åbne. Reglerne afgør det, ikke denne fil.
    if rules.should_open_alarm(data.humidity, open_alarm is not None):
        # Rød måling og ingen åben alarm: opret en (det er eventet "Anomaly Detected").
        open_alarm = Alarm(device_id=data.device_id, humidity=data.humidity, opened_at=now())
        session.add(open_alarm)
    elif open_alarm and rules.should_close_alarm(data.humidity):
        # Der er en åben alarm, og fugten er normal igen: luk (normalisér) den.
        open_alarm.closed_at = now()
        open_alarm = None  # så svaret nedenfor siger alarm_open: false

    session.commit()  # alt gemmes samlet (en transaktion), eller slet ikke
    # Svaret til Pi'en: farven til LED'en, og om der nu er en åben alarm.
    return {"status": color, "alarm_open": open_alarm is not None}


# --- Endpoint 2: de seneste målinger (kontrolcentret viser den nyeste) -------
# ?limit=20 i URL'en bestemmer, hvor mange der hentes. Kontrolcentret bruger limit=1.
# Query(ge=1, le=100): kun 1-100 er lovligt, ellers svarer FastAPI selv med 422.
@app.get("/measurements")
def list_measurements(limit: int = Query(20, ge=1, le=100), session: Session = Depends(get_session)):
    # Sortér efter id baglæns (desc), så den nyeste måling kommer først.
    return session.exec(select(Measurement).order_by(Measurement.id.desc()).limit(limit)).all()


# --- Endpoint 3: de 20 seneste alarmer (til alarmtabellen) -------------------
@app.get("/alarms")
def list_alarms(session: Session = Depends(get_session)):
    return session.exec(select(Alarm).order_by(Alarm.id.desc()).limit(20)).all()


# --- Endpoint 4: operatøren kvitterer ("jeg har set alarmen") ----------------
# {alarm_id} i stien bliver til parameteren alarm_id, fx POST /alarms/3/ack.
@app.post("/alarms/{alarm_id}/ack")
def acknowledge_alarm(alarm_id: int, session: Session = Depends(get_session)):
    alarm = session.get(Alarm, alarm_id)  # slå alarmen op på dens id
    if alarm is None:
        raise HTTPException(404, "Alarmen findes ikke")  # 404 = Not Found
    if alarm.acknowledged_at is not None:
        raise HTTPException(409, "Alarmen er allerede kvitteret")  # 409 = Conflict
    if alarm.closed_at is not None:
        # Fugten er allerede normal igen: der er ikke længere noget at kvittere for.
        raise HTTPException(409, "Alarmen er allerede lukket (normal igen)")
    alarm.acknowledged_at = now()  # kvittering lukker IKKE alarmen; det gør kun normal fugt
    session.commit()  # gem ændringen
    session.refresh(alarm)  # hent rækken igen, så svaret viser de gemte værdier
    return alarm


# --- Kontrolcentret: forsiden i browseren ------------------------------------
# include_in_schema=False: siden er ikke en del af API'et, så den skjules i Swagger.
@app.get("/", include_in_schema=False)
def control_center():
    # Path(__file__).parent er mappen, main.py ligger i.
    return FileResponse(Path(__file__).parent / "static" / "index.html")
