# Kodeguide: sådan virker løsningen

Læs filerne i denne rækkefølge. Hver fil kan forklares på et minut.

## 1. Den store tegning

```
Pi (pi.py)  --POST fugt-->  API (main.py)  --spørger-->  regler (rules.py)
     ^                          |
     |  svar: green/yellow/red  +--gemmer-->  PostgreSQL (db.py: measurement + alarm)
     +--------------------------+
Browser (index.html) --GET målinger/alarmer, POST kvittering--> API
```

Kun serveren træffer beslutninger. Pi'en og browseren viser bare, hvad serveren har sagt.

## 2. `rules.py`: reglen (hjertet)

Tre små funktioner, ingen database og intet netværk:

- `status(humidity)`: over 60 → `"red"`, fra 55 til og med 60 → `"yellow"`, ellers `"green"`.
- `should_open_alarm(humidity, alarm_already_open)`: kun ja, hvis rød **og** der ikke allerede er en åben alarm. Det forhindrer dubletter.
- `should_close_alarm(humidity)`: ja, hvis under 55. Mellemrummet 55–60 er *hysterese*: alarmen blinker ikke, hvis fugten vipper omkring 60.

**Spørgsmål til eksamen:** *Hvorfor lukker alarmen ikke ved 59?* Fordi den skulle åbne og lukke hele tiden, hvis fugten svinger mellem 59 og 61. Det svarer til en termostat.

## 3. `db.py`: databasen

- `Measurement` = én række pr. måling (eventet *Sensor Value Received*). Gemmer enhed, fugt, farve og tidspunkt.
- `Alarm` = én række pr. alarm (eventet *Anomaly Detected*). Tre tidspunkter fortæller historien: `opened_at` (åbnet), `acknowledged_at` (kvitteret), `closed_at` (normaliseret).
- `DATABASE_URL` bestemmer databasen. I Docker er det PostgreSQL; uden Docker en SQLite-fil.
- `get_session()` giver hver forespørgsel sin egen forbindelse og lukker den bagefter.

SQLModel betyder, at én Python-klasse både er tabellen og objektet i koden.

## 4. `main.py`: API'et

`POST /measurements` er hele flowet på 15 linjer:

1. **Event:** Pydantic-klassen `MeasurementIn` tjekker data (fugt skal være 0–100). Forkerte data afvises automatisk med HTTP 422.
2. Målingen gemmes med sin farve fra `rules.status()`.
3. **Beslutning:** find en åben alarm for enheden (`closed_at == None`), og spørg reglerne.
4. **Handling:** opret en ny alarm, eller luk den åbne.
5. `session.commit()` gemmer det hele på én gang (en *transaktion*): enten bliver alt gemt, eller intet.
6. Svaret `{"status": "red", "alarm_open": true}` fortæller Pi'en, hvilken farve LED'en skal have.

De andre endpoints:

- `GET /measurements?limit=20` og `GET /alarms`: nyeste først, til kontrolcentret.
- `POST /alarms/{id}/ack`: sætter `acknowledged_at`. Svarer 404, hvis alarmen ikke findes, og 409, hvis den allerede er kvitteret. Kvittering lukker **ikke** alarmen; det gør kun normal fugt.
- `GET /`: sender `static/index.html`.
- `/docs`: Swagger, som FastAPI laver automatisk ud fra koden.

`lifespan` opretter tabellerne én gang, når serveren starter.

## 5. `static/index.html`: kontrolcentret

Én fil med tre dele:

- **CSS** (øverst): farverne står ét sted i `:root`. Mørk tilstand skifter bare farverne.
- **HTML**: fugt-kortet, to grå *Fase 2 – mockup*-kort (lufttryk og rystelser, faste tal, ingen kode bagved) og alarmtabellen.
- **JavaScript** (nederst, ca. 45 linjer):
  - `loadHumidity()` henter den nyeste måling og farver kortet.
  - `loadAlarms()` bygger tabellen. Kun åbne, ukvitterede alarmer får en **Kvittér**-knap.
  - `ack(id)` sender kvitteringen og opdaterer tabellen.
  - `setInterval(refresh, 3000)` gentager hvert 3. sekund.

## 6. `pi/pi.py`: Raspberry Pi

En uendelig løkke hvert 5. sekund: læs fugt (`sense.get_humidity()`), send med `requests.post`, farv hele LED-displayet med `sense.clear(farve)`.
Blå betyder *ingen forbindelse*. Pi'en bestemmer ikke noget selv, så reglerne kun skal ændres ét sted.

## 7. Test og automatik

- `tests/test_mvp.py`: 5 tests (se tabellen *Strategi → regel → test* i `KRAV.md`). Hver test får en tom database i hukommelsen, så de kører på under et sekund.
- `postman/`: 5 kald, der gennemspiller hele alarmflowet mod den kørende Docker-stak.
- `Dockerfile`: bygger API'et i en container, der ikke kører som root.
- `docker-compose.yml`: to containere, `db` (PostgreSQL) og `api`. API'et venter, til databasen er klar (healthcheck).
- `.github/workflows/ci.yml`: pip-audit → pytest → Docker → Newman. Kører automatisk ved hvert push til `main`.
