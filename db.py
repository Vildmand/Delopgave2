"""db.py - databasen: to tabeller og en forbindelse.

Tabellerne:
    measurement  = hvert "Sensor Value Received"-event (input fra Pi'en)
    alarm        = hvert "Anomaly Detected"-event (output fra reglerne)

SQLModel er et lille lag oven på SQLAlchemy: én Python-klasse er både
tabeldefinitionen og det objekt, vi arbejder med i koden.

Hvilken database? Det styres af miljøvariablen DATABASE_URL:
    - I Docker peger den på PostgreSQL i sin egen container (se docker-compose.yml).
    - Uden Docker (fx når testene kører) bruges en lokal SQLite-fil.
"""

import os
from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fugt.db")
engine = create_engine(DATABASE_URL)


class Measurement(SQLModel, table=True):
    """Én fugtmåling, som Pi'en har sendt. Rækker ændres aldrig bagefter."""

    id: int | None = Field(default=None, primary_key=True)
    device_id: str
    humidity: float
    status: str  # green / yellow / red, beregnet af rules.status()
    received_at: datetime


class Alarm(SQLModel, table=True):
    """En alarm. Åben så længe closed_at er tom. Kvitteret når acknowledged_at er udfyldt."""

    id: int | None = Field(default=None, primary_key=True)
    device_id: str
    humidity: float  # den måling, der udløste alarmen
    opened_at: datetime
    acknowledged_at: datetime | None = None  # operatøren har set alarmen
    closed_at: datetime | None = None  # fugten er normal igen (under 55)


def create_tables() -> None:
    """Opret tabellerne, hvis de ikke findes. Kaldes én gang, når serveren starter."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Giv hver HTTP-forespørgsel sin egen databasesession (FastAPI 'dependency')."""
    with Session(engine) as session:
        yield session
