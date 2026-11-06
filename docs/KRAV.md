# Opgavens krav → hvor de er løst

Kilde: *Afleveringsopgave #2 – Teknisk MVP – REST API Microservice løsning* og *Casebeskrivelse (IIS)*.
Kun det, opgaven kræver, er bygget. Alt andet er flyttet til refleksionen som "vejen frem".

## Scenariet (afsnit 2)

| Krav | Løst i |
|---|---|
| Domæne: Predictive Maintenance / notifikation (core subdomain) | IIS Managed Services, 24/7 overvågning fra kontrolcentret i Aalborg (casen s. 2) |
| Event: Sensor Value Received | `POST /measurements` → række i tabellen `measurement` |
| Event: Anomaly Detected | `rules.should_open_alarm()` → række i tabellen `alarm` |
| Beslutning: threshold-check | `rules.status()` (55 / 60 %RH) |
| Handling: alarm/notifikation | Alarm i kontrolcentret + LED på Pi'en skifter farve |
| Forretningsbehov | Færre uventede stop: medarbejderen ser afvigelsen i tide (VS7 fra delopgave 1) |

## Det tekniske produkt (afsnit 3)

| Krav | Løst i | Bevis |
|---|---|---|
| REST API, der kan tilgås fra remote computer (IoT device) | `main.py` med `--host 0.0.0.0`, `pi/pi.py` sender over netværket | Pi'en på 192.168.0.106 → PC på 192.168.0.103:8000 |
| Håndtering af events (input → behandling → output) | `receive_measurement()` i `main.py` | Test 2–5, Postman 1–5 |
| Logik relateret til domænet (validering, hændelse, beslutning) | Validering: `MeasurementIn` (0–100 %RH). Beslutning: `rules.py` | Test 1 og 422-svar ved forkerte data |
| Persistering af domain events og output i **separat** database | PostgreSQL i sin egen container (`docker-compose.yml`), tabellerne i `db.py` | `psql`-udtræk i videoen |
| CI/CD med GitHub Actions | `.github/workflows/ci.yml` | Grøn kørsel på GitHub |
| Tech stack i lokal Docker container | `Dockerfile` + `docker-compose.yml` | `docker compose up --build` |
| GitHub repo med REST API-kode og CI/CD-kode | Dette repo | |

## Demonstration (afsnit 4, video)

| Krav | Hvor |
|---|---|
| Hvordan løsningen køres op lokalt | `docker compose up --build` (README) |
| Hvor REST API er dokumenteret | Swagger på `/docs` + tabellen i README |
| Test med Postman, og at data persisteres | `postman/` + `psql` i db-containeren |

## Bevidst fravalgt (ikke krævet)

Hændelseslog-tabel, flere lag (api/application/domain/infrastructure), migrationer, rækkelås,
kø på Pi'en, simulering, login/API-nøgler, tryk og rystelser. Alt findes i den store udgave (RaspPI)
og er beskrevet i rapportens refleksion.

## Strategi → regel → test

| Fra delopgave 1 (strategi) | Regel i koden | Test |
|---|---|---|
| Evne: følge hver enheds tilstand | `status()`: grøn < 55, gul 55–60, rød > 60 | `test_1_green_yellow_red` |
| Event Storming: "Fejl rapporteret" → "Generer alert" | `should_open_alarm()`: rød → alarm | `test_2_alarm_created_over_60` |
| Undgå alarmtræthed i kontrolcentret | Ingen ny alarm, mens en er åben | `test_3_no_duplicate_alarm` |
| Medarbejderen tager ansvar for alarmen | `POST /alarms/{id}/ack` | `test_4_acknowledge` |
| Alarmen må ikke blinke ved grænsen (hysterese) | `should_close_alarm()`: lukkes først under 55 | `test_5_normalization_under_55` |
