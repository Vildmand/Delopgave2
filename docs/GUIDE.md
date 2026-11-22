# Guide: kør fugt-MVP'en fra start til slut

Trin for trin på Windows med Docker Desktop. Hver kommando køres i PowerShell.
Koden er forklaret i `KODEGUIDE.md`, og opgavens krav er listet i `KRAV.md`.

## 1. Gå til projektmappen

Alle kommandoer skal køres herfra. Ellers svarer Docker `no configuration file provided`,
og newman svarer `ENOENT`.

```powershell
cd C:\Users\nickl\Desktop\Kea\Sem6\Newrasp
```

## 2. Start API + database

```powershell
docker compose up -d --build
docker compose ps
```

Alle tre containere skal stå som `Up`:

| Container | Port | Hvad |
|---|---|---|
| `newrasp-api-1` | 8000 | REST API'et (FastAPI) |
| `newrasp-db-1` | 5432 (kun inde i Docker) | PostgreSQL, `(healthy)` |
| `newrasp-grafana-1` | 3000 | Grafana-dashboard (læser kun fra databasen) |

Tjek, at API'et svarer. Det giver `[]`, når databasen er tom:

```powershell
curl.exe http://localhost:8000/alarms
```

## 3. Kør testene

**Postman (newman)** tester hele alarmflowet mod den kørende stak:

```powershell
npx --yes newman@6 run postman/fugt-mvp.postman_collection.json
```

Forventet: `requests 5 / failed 0` og `assertions 5 / failed 0`.
npm-advarslerne om `deprecated` er harmløse.

**Unit-tests (pytest)** kører uden Docker mod en SQLite-database i hukommelsen:

```powershell
pip install -r requirements.txt -r requirements-dev.txt
pytest -v
```

## 4. Se kontrolcentret

- Kontrolcentret: http://localhost:8000
- Swagger (prøv endpoints i browseren): http://localhost:8000/docs
- Grafana (fugt over tid, åbne alarmer, MTTA): http://localhost:3000

Send en måling i hånden og se den dukke op:

```powershell
curl.exe -X POST http://localhost:8000/measurements -H "Content-Type: application/json" -d '{\"device_id\":\"test\",\"humidity\":62}'
```

62 %RH er rød og åbner en alarm. Tryk **Kvittér** i kontrolcentret.
Send derefter 50 %RH, så lukkes alarmen.

## 5. Tilslut Raspberry Pi'en

De detaljerede trin og Pi-fejlfinding står i `PI-GUIDE.md`. Kort fortalt:

1. Find PC'ens IP med `ipconfig` (IPv4 under Wi-Fi).
2. Kun første gang: hvis Pi'en ikke kan nå PC'en, så tillad port 8000 i Windows Firewall
   (PowerShell som administrator):
   ```powershell
   New-NetFirewallRule -DisplayName "Fugt-MVP API" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
   ```
3. `scp pi\pi.py nicklas@NicklasRPI.local:~/`, `ssh` ind på Pi'en og kør
   `API_URL=http://<PC-IP>:8000 python3 pi.py`.
4. Pust på Sense HAT'en. LED'en skifter fra grøn over gul til rød, og alarmen
   dukker op i kontrolcentret.

| LED | Betyder |
|---|---|
| Grøn | under 55 %RH |
| Gul | 55-60 %RH, advarsel |
| Rød | over 60 %RH, alarm åbnet |
| Blå | Pi'en kan ikke nå serveren |

**Tip:** Viser displayet andre mønstre, eller blinker det mellem farver, så kører der
to programmer på Pi'en på samme tid. Find dem, stop dem, og start `pi.py` én gang:

```bash
pgrep -af python
pkill -f python3
API_URL=http://<PC-IP>:8000 python3 pi.py
```

## 6. Stop igen

```powershell
docker compose down      # stop, data bevares
docker compose down -v   # stop og SLET databasen
```

## Fejlfinding

| Fejl | Årsag | Løsning |
|---|---|---|
| `no configuration file provided: not found` | Kørt fra forkert mappe | `cd` til Newrasp (trin 1) |
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | En anden container bruger port 8000 | `docker ps`, stop den gamle (`docker stop <navn>`), kør `docker compose up -d` igen |
| `newrasp-api-1` stopper med `failed to resolve host 'db'` | Følgefejl af port-konflikten | Ret port-konflikten, kør `docker compose up -d` igen |
| newman: `ECONNREFUSED 127.0.0.1:8000` | API'et kører ikke endnu | Vent til `curl.exe http://localhost:8000/alarms` svarer, kør newman igen |
| Pi'ens LED er blå | Pi'en kan ikke nå PC'en | Se `PI-GUIDE.md` (IP, netværk, firewall) |
| Se hvad API'et laver | | `docker compose logs -f api` |
