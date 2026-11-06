"""db.py - databasen: to tabeller og en forbindelse.

Tabellerne:
    measurement  = hvert "Sensor Value Received"-event (input fra Pi'en)
    alarm        = hvert "Anomaly Detected"-event (output fra reglerne)

SQLModel er et lille lag oven på SQLAlchemy: én Python-klasse er både
tabeldefinitionen og det objekt, vi arbejder med i koden. Vi skriver altså
ikke SQL i hånden; SQLModel laver CREATE TABLE, INSERT og SELECT for os.

Hvilken database? Det styres af miljøvariablen DATABASE_URL:
    - I Docker peger den på PostgreSQL i sin egen container (se docker-compose.yml).
      Det opfylder opgavens krav om en SEPARAT database.
    - Uden Docker (fx når man prøver koden hurtigt) bruges en lokal SQLite-fil.
"""

import os  # læser miljøvariabler
from datetime import datetime  # typen på tidsstemplerne

from sqlmodel import Field, Session, SQLModel, create_engine

# Læs DATABASE_URL. Findes den ikke, bruges filen fugt.db i samme mappe.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///fugt.db")
# "engine" er forbindelsen til databasen. Den oprettes én gang og deles af alle.
engine = create_engine(DATABASE_URL)


# table=True betyder: lav en rigtig tabel i databasen ud fra klassen.
class Measurement(SQLModel, table=True):
    """Én fugtmåling, som Pi'en har sendt. Rækker ændres aldrig bagefter."""

    id: int | None = Field(default=None, primary_key=True)  # databasen tildeler 1, 2, 3 ...
    device_id: str  # hvilken Pi målingen kom fra, fx "pi-01"
    humidity: float  # målingen i %RH
    status: str  # green / yellow / red, beregnet af rules.status()
    received_at: datetime  # hvornår serveren modtog målingen (UTC)


class Alarm(SQLModel, table=True):
    """En alarm. Åben så længe closed_at er tom. Kvitteret når acknowledged_at er udfyldt.

    De tre tidspunkter fortæller hele alarmens historie:
    opened_at (åbnet) -> acknowledged_at (set af operatøren) -> closed_at (normal igen).
    """

    id: int | None = Field(default=None, primary_key=True)  # databasen tildeler id
    device_id: str  # hvilken Pi alarmen gælder
    humidity: float  # den måling, der udløste alarmen
    opened_at: datetime  # hvornår alarmen blev åbnet
    acknowledged_at: datetime | None = None  # operatøren har set alarmen (None = ikke endnu)
    closed_at: datetime | None = None  # fugten er normal igen (under 55); None = stadig åben


def create_tables() -> None:
    """Opret tabellerne, hvis de ikke findes. Kaldes én gang, når serveren starter."""
    SQLModel.metadata.create_all(engine)  # findes tabellen allerede, sker der intet


def get_session():
    """Giv hver HTTP-forespørgsel sin egen databasesession (FastAPI 'dependency').

    "with" sørger for, at sessionen lukkes igen, når forespørgslen er færdig.
    "yield" giver sessionen til endpointet og venter, til det er færdigt.
    Testene udskifter denne funktion med en, der bruger en tom testdatabase.
    """
    with Session(engine) as session:
        yield session
