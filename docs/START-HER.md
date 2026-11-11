# Start her: fugt-MVP på én side

**Hvad er det?** En lille REST API-løsning til IIS Managed Services (delopgave 2, gruppe 9).
En Raspberry Pi med Sense HAT måler luftfugtighed og sender den til en server i Docker.
Serveren afgør grøn (under 55 %RH), gul (55–60) eller rød (over 60). Ved rød åbnes en alarm,
som en medarbejder ser i kontrolcentret og kvitterer for. Alarmen lukker selv under 55 %RH.

**Kæden opgaven kræver:** hændelse (*Sensor Value Received*) → beslutning (reglen i `rules.py`) → handling (alarm = *Anomaly Detected*, LED bliver rød).

## Læs i denne rækkefølge (ca. 30 minutter)

Filerne ligger i zip-pakken i mapperne 1–5. I repoet ligger de samme ting i `docs/`.

| # | I pakken | I repoet | Hvad det er |
|---|---|---|---|
| 1 | `1-praesentation/` | `docs/praesentation.pdf` / `.pptx` | 11 slides: hvad vi byggede og hvorfor. Talenoter under hver slide |
| 2 | `2-rapport/` | `docs/RAPPORT.md` | Den endelige 7-siders rapport (pdf og docx), rettet efter feedbacken på delopgave 1: strategi og målbare mål, bounded contexts og teknisk arkitektur. Bilag med kode, diagrammer og begreber |
| 3 | `3-diagrammer/` | `docs/img/diagram-simpel-*.png` | 1 deployment · 2 regler og alarmflow · 3 én måling start-slut · 4 CI/CD · 5 datamodel · 6 vejen frem · 7 bounded contexts og context map · 8 teknisk arkitektur og mønstre |
| 4 | `4-dokumenter/KODEGUIDE` | `docs/KODEGUIDE.md` | Gennemgang af hver fil, og hvorfor koden er skrevet sådan |
| 5 | `5-kodebilleder/` | `docs/img/01-…11-*.png` | De vigtigste kodestykker som billeder, klar til slides |
| 6 | `4-dokumenter/KRAV` | `docs/KRAV.md` | Opgavens krav, og hvilken fil der opfylder hvert krav |
| 7 | `4-dokumenter/PI-GUIDE` | `docs/PI-GUIDE.md` | Trin for trin: få Pi'en til at sende, med fejlfinding |
| 8 | `4-dokumenter/VIDEOMANUSKRIPT` | `docs/VIDEOMANUSKRIPT.md` | Hvad der vises og siges i den ca. 5 minutter lange video |

Koden: https://github.com/Vildmand/Delopgave2 ·
Grøn CI-kørsel: https://github.com/Vildmand/Delopgave2/actions/runs/42225474539

## Kør det selv

Kræver Docker Desktop. I repo-mappen:

```powershell
docker compose up --build
```

Åbn http://localhost:8000 (kontrolcentret) og http://localhost:8000/docs (Swagger). Stop med `Ctrl+C`.
`docker compose down -v` sletter også databasen.

På Pi'en (udskift IP med PC'ens IP på samme Wi-Fi):

```bash
API_URL=http://192.168.0.103:8000 python3 pi.py
```

Pust på Sense HAT'en: LED'en bliver rød, og alarmen dukker op i kontrolcentret. Uden Pi: importér
`postman/fugt-mvp.postman_collection.json` i Postman og tryk **Run collection** (5 kald, hele alarmflowet).

## Hvorfor så simpelt? (scope-beslutningen)

Vi byggede først en stor udgave i [miemosberg2201/RaspPI](https://github.com/miemosberg2201/RaspPI):
tre måletyper, hændelseslog, kode i lag og 153 tests. Den virkede, men var svær at forklare på få minutter.
Derfor byggede vi en **simpel MVP** i et nyt repo: kun fugt live, fem filer, 5 tests (strategi → regel → test),
og alle opgavens krav er stadig opfyldt. Lufttryk og rystelser vises som grå *Fase 2 – mockup*-kort.
Den store udgave står urørt og er **vejen frem** (diagram 6 og rapportens afsnit 6.3):
robust regel → hændelseslog → flere måletyper → lag og migrationer → kø på Pi'en → login, HTTPS og Azure.
