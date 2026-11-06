"""De 5 tests. Kør: pytest -v

Testene bruger en tom SQLite-database i hukommelsen, så de kører på et sekund
og ikke kræver Docker. API'et kaldes præcis som Pi'en og Postman gør det.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import rules
from db import get_session
from main import app


@pytest.fixture
def client():
    # Ny, tom database til hver test, så testene ikke påvirker hinanden.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def test_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = test_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def send(client, humidity):
    return client.post("/measurements", json={"device_id": "pi-01", "humidity": humidity}).json()


def test_1_green_yellow_red():
    assert rules.status(48) == "green"
    assert rules.status(55) == "yellow"
    assert rules.status(60) == "yellow"
    assert rules.status(60.1) == "red"


def test_2_alarm_created_over_60(client):
    assert send(client, 62) == {"status": "red", "alarm_open": True}
    alarms = client.get("/alarms").json()
    assert len(alarms) == 1 and alarms[0]["humidity"] == 62


def test_3_no_duplicate_alarm(client):
    for value in (62, 65, 61):
        send(client, value)
    assert len(client.get("/alarms").json()) == 1


def test_4_acknowledge(client):
    send(client, 62)
    alarm_id = client.get("/alarms").json()[0]["id"]
    assert client.post(f"/alarms/{alarm_id}/ack").json()["acknowledged_at"] is not None
    assert client.post(f"/alarms/{alarm_id}/ack").status_code == 409  # ikke to gange
    assert client.post("/alarms/999/ack").status_code == 404


def test_5_normalization_under_55(client):
    send(client, 62)
    assert send(client, 57)["alarm_open"] is True  # gul: alarmen er stadig åben
    assert send(client, 50) == {"status": "green", "alarm_open": False}
    assert client.get("/alarms").json()[0]["closed_at"] is not None
