# Fugt-MVP: fra sensor til alarm

En lille REST API-løsning til Intelligent IoT Solutions A/S (IIS), Managed Services.
En Raspberry Pi med Sense HAT måler luftfugtighed og sender den til serveren.
Serveren afgør grøn, gul eller rød, åbner en alarm over 60 %RH og lukker den igen under 55 %RH.
En medarbejder ser alarmen i kontrolcentret og kvitterer.

**Event → beslutning → handling:** `Sensor Value Received` → regel i `rules.py` → `Anomaly Detected` (alarm gemt i databasen + LED skifter farve).

## Filerne

| Fil | Hvad den gør | Linjer |
|---|---|---|
| `main.py` | REST API'et: 4 endpoints + kontrolcentret | ca. 100 |
| `rules.py` | Reglerne: grøn/gul/rød, åbn og luk alarm | ca. 40 |
| `db.py` | Databasen: tabellerne `measurement` og `alarm` | ca. 50 |
| `static/index.html` | Kontrolcentret: live fugt, alarmer, Kvittér-knap, grå mockup for fase 2 | ca. 130 |
| `pi/pi.py` | Programmet på Pi'en: læs fugt, send, farv LED | ca. 45 |
| `tests/test_mvp.py` | De 5 tests | ca. 65 |
| `postman/` | Postman-samling med 5 kald (hele alarmflowet) | |
| `Dockerfile`, `docker-compose.yml` | Kør API + PostgreSQL i hver sin container | |
| `.github/workflows/ci.yml` | CI/CD på GitHub Actions | |
| `docs/` | KODEGUIDE (forklaring af koden) og KRAV (opgavens krav → fil) | |

Kommentarerne i koden er en del af dokumentationen. Start med `docs/KODEGUIDE.md`.

## Kør løsningen (Windows, Docker Desktop)

```powershell
docker compose up --build
```

Åbn derefter:

- Kontrolcentret: http://localhost:8000
- Swagger (API-dokumentation): http://localhost:8000/docs

Stop med `Ctrl+C`. Slet også databasen med `docker compose down -v`.

## Kør på Pi'en

Kopiér filen til Pi'en og start den med PC'ens IP-adresse:

```powershell
scp pi\pi.py nicklas@NicklasRPI.local:~/
ssh nicklas@NicklasRPI.local
API_URL=http://192.168.0.103:8000 python3 pi.py
```

Pust på Sense HAT'en for at få fugten over 60 %RH. LED'en bliver rød, og alarmen dukker op i kontrolcentret.
Trin for trin med fejlfinding: `docs/PI-GUIDE.md`.

## Test

```powershell
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

Postman: importér `postman/fugt-mvp.postman_collection.json` og tryk **Run collection** (mens Docker kører).

## API

| Metode | Adresse | Hvad |
|---|---|---|
| POST | `/measurements` | Pi'en sender `{"device_id": "pi-01", "humidity": 48.2}`. Svar: `{"status": "green", "alarm_open": false}` |
| GET | `/measurements` | De seneste målinger (nyeste først) |
| GET | `/alarms` | De seneste alarmer |
| POST | `/alarms/{id}/ack` | Kvittér for en alarm (404 hvis den ikke findes, 409 hvis allerede kvitteret) |

## CI/CD

GitHub Actions kører: pip-audit (sårbarheder) → de 5 tests → byg og start Docker (API + PostgreSQL) → Postman via Newman.
Den kører automatisk ved hvert push til `main` og ved pull requests. Den kan også startes i hånden under **Actions → CI → Run workflow**.

## Den store udgave

Den fulde løsning (tre måletyper, hændelseslog, 153 tests) ligger urørt i det gamle repo
[miemosberg2201/RaspPI](https://github.com/miemosberg2201/RaspPI). Den viser vejen frem (se rapportens refleksion).
