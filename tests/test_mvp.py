"""De 5 tests. Kør: pytest -v

Testene bruger en tom SQLite-database i hukommelsen, så de kører på et sekund
og ikke kræver Docker. API'et kaldes præcis som Pi'en og Postman gør det.

Hver test svarer til en regel (se docs/KRAV.md, "strategi -> regel -> test"):
    1. farverne grøn/gul/rød (+ validering)   2. alarm over 60   3. ingen dublet-alarm
    4. kvittering (404/409)                   5. normalisering under 55

Hver test prøver også grænsen lige ved siden af (fx 54,9 og 55), så en forkert
ændring af reglerne får en test til at fejle.
"""

import pytest  # testværktøjet
from fastapi.testclient import TestClient  # kalder API'et uden at starte en rigtig server
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool  # én fælles forbindelse, så in-memory-databasen ikke forsvinder

import rules
from db import get_session
from main import app


@pytest.fixture
def client():
    """En "fixture" er forberedelse, som pytest kører før hver test, der beder om "client"."""
    # Ny, tom database til hver test, så testene ikke påvirker hinanden.
    # "sqlite://" uden filnavn = databasen ligger kun i hukommelsen.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)  # opret tabellerne i testdatabasen

    def test_session():
        with Session(engine) as session:
            yield session

    # Byt den rigtige database ud med testdatabasen, kun mens testen kører.
    app.dependency_overrides[get_session] = test_session
    yield TestClient(app)  # testen får klienten her
    app.dependency_overrides.clear()  # ryd op efter testen


def send(client, humidity, device_id="pi-01"):
    """Hjælper: send én måling, som Pi'en ville gøre, og returnér svaret som dict."""
    return client.post("/measurements", json={"device_id": device_id, "humidity": humidity}).json()


def test_1_green_yellow_red(client):
    # Reglen alene, uden API og database. Begge sider af grænserne 55 og 60 testes.
    assert rules.status(48) == "green"
    assert rules.status(54.9) == "green"  # lige under 55: stadig grøn
    assert rules.status(55) == "yellow"  # præcis 55: gul
    assert rules.status(60) == "yellow"  # præcis 60: stadig gul
    assert rules.status(60.1) == "red"  # lige over 60: rød
    # Validering: tal uden for 0-100 %RH afvises med 422, og intet gemmes.
    assert client.post("/measurements", json={"humidity": 150}).status_code == 422
    assert client.post("/measurements", json={"humidity": -5}).status_code == 422
    assert client.get("/measurements").json() == []


def test_2_alarm_created_over_60(client):
    # En rød måling skal give rødt svar og præcis én alarm i databasen.
    assert send(client, 62) == {"status": "red", "alarm_open": True}
    alarms = client.get("/alarms").json()
    assert len(alarms) == 1 and alarms[0]["humidity"] == 62
    # Målingen, der udløste alarmen, er gemt sammen med den (samme transaktion).
    assert client.get("/measurements").json()[0]["status"] == "red"
    # Præcis 60 er kun gul og må ikke give en alarm (en anden Pi, så den starter uden alarm).
    assert send(client, 60, "pi-02") == {"status": "yellow", "alarm_open": False}


def test_3_no_duplicate_alarm(client):
    # Tre røde målinger i træk må kun give én alarm.
    for value in (62, 65, 61):
        send(client, value)
    assert len(client.get("/alarms").json()) == 1
    # "Ingen dublet" gælder pr. enhed: en anden Pi får sin egen alarm.
    assert send(client, 70, "pi-02")["alarm_open"] is True
    assert len(client.get("/alarms").json()) == 2


def test_4_acknowledge(client):
    # Kvittering virker én gang. Anden gang: 409. Ukendt alarm: 404.
    send(client, 62)
    alarm_id = client.get("/alarms").json()[0]["id"]
    acknowledged = client.post(f"/alarms/{alarm_id}/ack").json()
    assert acknowledged["acknowledged_at"] is not None
    assert acknowledged["closed_at"] is None  # kvittering lukker IKKE alarmen
    assert client.post(f"/alarms/{alarm_id}/ack").status_code == 409  # ikke to gange
    assert client.post("/alarms/999/ack").status_code == 404
    # En alarm, der er lukket uden kvittering, kan ikke kvitteres bagefter (409).
    send(client, 70, "pi-02")
    send(client, 50, "pi-02")
    closed_id = client.get("/alarms").json()[0]["id"]
    assert client.post(f"/alarms/{closed_id}/ack").status_code == 409


def test_5_normalization_under_55(client):
    # Gul (57) og præcis 55 lukker ikke alarmen; først under 55 lukker den (hysterese).
    send(client, 62)
    assert send(client, 57)["alarm_open"] is True  # gul: alarmen er stadig åben
    assert send(client, 55)["alarm_open"] is True  # præcis 55 er ikke "under 55"
    assert send(client, 54.9) == {"status": "green", "alarm_open": False}
    assert client.get("/alarms").json()[0]["closed_at"] is not None
