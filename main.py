"""main.py - REST API'et (FastAPI). Start: uvicorn main:app --host 0.0.0.0

Flowet "event -> beslutning -> handling" sker i POST /measurements:
    1. Event:      Pi'en sender en fugtmåling (Sensor Value Received).
    2. Beslutning: rules.py afgør grøn/gul/rød, og om en alarm skal åbnes eller lukkes.
    3. Handling:   målingen og evt. alarmen gemmes i databasen (Anomaly Detected),
                   og svaret fortæller Pi'en, hvilken farve LED'en skal vise.

Endpoints:
    POST /measurements          modtag en måling fra Pi'en
    GET  /measurements          de seneste målinger (til kontrolcentret)
    GET  /alarms                de seneste alarmer
    POST /alarms/{id}/ack       operatøren kvitterer for en alarm
    GET  /                      kontrolcentret (static/index.html)
    GET  /docs                  Swagger: automatisk API-dokumentation fra FastAPI
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

import rules
from db import Alarm, Measurement, create_tables, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  # køres én gang ved opstart
    yield


app = FastAPI(
    title="Fugt-MVP",
    description="Fugtovervågning for IIS Managed Services: måling -> regel -> alarm.",
    lifespan=lifespan,
)


class MeasurementIn(BaseModel):
    """Det, Pi'en sender. Pydantic afviser selv ugyldige værdier med HTTP 422."""

    device_id: str = Field(default="pi-01", min_length=1, max_length=50)
    humidity: float = Field(ge=0, le=100, description="Relativ luftfugtighed i %RH")


def now() -> datetime:
    return datetime.now(timezone.utc)


@app.post("/measurements", status_code=201)
def receive_measurement(data: MeasurementIn, session: Session = Depends(get_session)):
    # 1. Event: gem målingen sammen med dens farve.
    color = rules.status(data.humidity)
    session.add(Measurement(device_id=data.device_id, humidity=data.humidity, status=color, received_at=now()))

    # 2. Beslutning: er der allerede en åben alarm for denne Pi?
    open_alarm = session.exec(
        select(Alarm).where(Alarm.device_id == data.device_id, Alarm.closed_at == None)  # noqa: E711
    ).first()

    # 3. Handling: åbn en ny alarm eller luk den åbne.
    if rules.should_open_alarm(data.humidity, open_alarm is not None):
        open_alarm = Alarm(device_id=data.device_id, humidity=data.humidity, opened_at=now())
        session.add(open_alarm)
    elif open_alarm and rules.should_close_alarm(data.humidity):
        open_alarm.closed_at = now()
        open_alarm = None

    session.commit()  # alt gemmes samlet, eller slet ikke
    return {"status": color, "alarm_open": open_alarm is not None}


@app.get("/measurements")
def list_measurements(limit: int = 20, session: Session = Depends(get_session)):
    return session.exec(select(Measurement).order_by(Measurement.id.desc()).limit(limit)).all()


@app.get("/alarms")
def list_alarms(session: Session = Depends(get_session)):
    return session.exec(select(Alarm).order_by(Alarm.id.desc()).limit(20)).all()


@app.post("/alarms/{alarm_id}/ack")
def acknowledge_alarm(alarm_id: int, session: Session = Depends(get_session)):
    alarm = session.get(Alarm, alarm_id)
    if alarm is None:
        raise HTTPException(404, "Alarmen findes ikke")
    if alarm.acknowledged_at is not None:
        raise HTTPException(409, "Alarmen er allerede kvitteret")
    alarm.acknowledged_at = now()
    session.commit()
    session.refresh(alarm)
    return alarm


@app.get("/", include_in_schema=False)
def control_center():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
