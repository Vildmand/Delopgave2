# Videomanuskript: Fra sensor til alarm (ca. 5 minutter)

Opgaven (afsnit 4) siger, at videoen skal vise tre ting:

1. **Hvordan løsningen køres op lokalt** af en MVP-bruger
2. **Hvor REST API'et er dokumenteret** (GitHub og/eller Swagger)
3. **At det virker via Postman, og at data gemmes i databasen**

Scene 3, 5, 6 og 7 dækker de tre krav. Resten viser domænet, reglen, Pi'en (remote IoT device), driften og CI/CD,
så videoen også rammer vurderingskriterierne "sammenhæng" og "kobling mellem domæne og teknik".

Teksten under **Sig** er skrevet til at blive sagt højt. Brug den som støtte, ikke som noget, der skal læses op ord for ord.
Det er helt fint at sige "øh" og at formulere det med egne ord. Ca. 700 ord svarer til godt 5 minutter i roligt tempo.

---

## Før du trykker optag (tjekliste)

| Hvad | Hvordan |
|---|---|
| Docker kører | `docker compose up --build` i repo-mappen. Tjek med `docker compose ps`: tre containere (`db`, `api`, `grafana`) |
| Behold dataene | Kør **ikke** `docker compose down -v` lige før. Grafana ser bedst ud med lidt historik |
| PC'ens IP | `ipconfig` → Wi-Fi IPv4 (sidst 192.168.0.103) |
| Pi'en sender | `ssh nicklas@NicklasRPI.local` → `API_URL=http://<pc-ip>:8000 python3 pi.py`. LED'en skal være grøn, ikke blå |
| Faner i browseren | 1: rapportens figur 1 og 2 i bilag E (eller `docs/praesentation.pdf`) · 2: GitHub-repoet · 3: `localhost:8000/docs` · 4: `localhost:8000` (kontrolcentret) · 5: `localhost:3000` (Grafana) · 6: GitHub → Actions (grøn kørsel) |
| Postman | Samlingen `postman/fugt-mvp.postman_collection.json` er importeret, og runneren er klar |
| Terminaler | Én til Docker/psql, én med SSH til Pi'en |
| Skærm | Zoom browseren til ca. 125 %, så tekst kan læses i videoen. Luk notifikationer |

---

## Scene 1 · Problemet og domænet (0:00–0:35)

**Krav:** Afsnit 2 (domæne, core subdomain, forretningsbehov) · vurdering: kobling mellem domæne og teknik
**Vis:** Rapportens figur 1 i bilag E (Event Storming øverst, context map nederst)

**Sig:**
> Hej. Vi er gruppe 9, og vi har bygget et teknisk MVP for Intelligent IoT Solutions, nærmere bestemt Managed Services, hvor kontrolcentret overvåger kundernes udstyr døgnet rundt.
> Problemet er, at for høj luftfugtighed kan ødelægge udstyr, og det opdager man tit først, når noget går i stykker.
> Så vi har lavet det, opgaven kalder predictive maintenance: vi måler fugten, og når den bliver for høj, får medarbejderen en alarm, før det bliver til et stop.
> Det her er vores context map fra delopgave 1. MVP'en bygger de to vigtigste dele: "Enhed og måling" og "Overvågning og alarm".

---

## Scene 2 · Arkitekturen: event, beslutning, handling (0:35–1:05)

**Krav:** Afsnit 2 (event-flow, regellogik) · vurdering: klarhed i teknisk arkitektur
**Vis:** Rapportens figur 2 i bilag E (teknisk arkitektur). Peg med musen på Pi → API → PostgreSQL → kontrolcenter, mens du siger det

**Sig:**
> Sådan hænger det sammen. En Raspberry Pi med en Sense HAT måler fugten og sender den over Wi-Fi til vores REST API.
> Det er eventet "Sensor Value Received".
> API'et tjekker værdien mod en grænse. Over 60 procent er det rødt, og så åbner vi en alarm. Det er "Anomaly Detected".
> Handlingen er, at alarmen dukker op i kontrolcentret, og at LED'en på Pi'en bliver rød.
> Alt bliver gemt i en PostgreSQL-database, der kører for sig selv.

---

## Scene 3 · Sådan kører man det op (1:05–1:30)

**Krav:** Afsnit 4, punkt 1 (køres op lokalt) · afsnit 3 (lokal Docker container, separat database)
**Vis:** Terminal: `docker compose up --build` (eller klip til at den er færdig), derefter `docker compose ps` med de tre containere

**Sig:**
> Hvis man vil prøve løsningen, skal man kun have Docker. Man kloner repoet og skriver `docker compose up --build`.
> Så starter tre containere: databasen, vores API og Grafana.
> Databasen har sin egen container og er ikke åben udadtil. Kun API'et kan snakke med den.

---

## Scene 4 · Koden og reglen (1:30–2:00)

**Krav:** Afsnit 3 (GitHub-repo med API-kode, logik relateret til domænet)
**Vis:** GitHub-repoet: filoversigten og README, klik ind i `rules.py`

**Sig:**
> Her er repoet på GitHub. Serveren er bevidst holdt lille: tre Python-filer.
> Selve reglen ligger her i rules.py. Over 60 er rødt, mellem 55 og 60 er gult, og under 55 er grønt.
> Det smarte er, at alarmen først lukker igen under 55. Ellers ville den blinke til og fra, hvis fugten lå og vippede omkring 60.
> Al koden har danske kommentarer, og der er en kodeguide i docs-mappen.

---

## Scene 5 · Hvor API'et er dokumenteret (2:00–2:35)

**Krav:** Afsnit 4, punkt 2 (dokumentation i GitHub og Swagger) · afsnit 3 (validering)
**Vis:** Scroll kort ned til API-tabellen i README. Skift til `localhost:8000/docs`. Åbn **POST /measurements** → *Try it out* → sæt `"humidity": 150` → *Execute* → vis svaret 422

**Sig:**
> API'et er dokumenteret to steder. I README'en på GitHub, og i Swagger, som FastAPI laver automatisk ud fra koden.
> Der er fire endpoints: sende en måling, hente målinger, hente alarmer og kvittere for en alarm.
> Jeg prøver lige at sende noget forkert: en fugtighed på 150 procent.
> Så siger API'et 422 og forklarer hvorfor. Kun 0 til 100 er gyldigt, så den måling bliver aldrig gemt.

---

## Scene 6 · Test med Postman (2:35–3:10)

**Krav:** Afsnit 4, punkt 3 (funktionalitet testet med Postman) · afsnit 3 (input, behandling, output)
**Vis:** Postman: åbn samlingen, vis de fem navne kort, tryk **Run collection** → vis at alle tests er grønne. Klik evt. ind på kald 2 og vis svaret `"status": "red", "alarm_open": true`

**Sig:**
> Så tester vi hele flowet i Postman. Samlingen har fem kald, der følger en alarm fra start til slut.
> Først en normal måling, som giver grøn. Så en høj måling på 62, som giver rød og åbner en alarm.
> Vi henter alarmen, kvitterer for den, og til sidst sender vi en normal måling, som lukker den igen.
> Og alle fem er grønne.

---

## Scene 7 · Data i databasen (3:10–3:35)

**Krav:** Afsnit 4, punkt 3 (data persisteres) · afsnit 3 (persistering af domain events og output i separat database)
**Vis:** Terminal:
```
docker compose exec db psql -U fugt -c "select * from measurement order by id desc limit 5;" -c "select * from alarm order by id desc limit 3;"
```

**Sig:**
> Og for at vise, at det rent faktisk er gemt, kigger jeg direkte i PostgreSQL.
> Her er målingerne fra Postman, med farven, som serveren har givet dem.
> Og her er alarmen. Den har et tidspunkt for, hvornår den blev åbnet, hvornår den blev kvitteret, og hvornår den blev lukket.
> Det er dem, vi bruger til at måle, hvor hurtigt kontrolcentret reagerer.

---

## Scene 8 · Den rigtige Pi (3:35–4:15)

**Krav:** Afsnit 3, punkt 1 (REST API tilgået fra remote computer / IoT device) · hele event → beslutning → handling live
**Vis:** Del skærmen: kontrolcentret (`localhost:8000`) til venstre, telefonvideo eller webcam af Pi'en til højre (eller klip mellem dem). Pust på Sense HAT'en → LED rød → alarmen dukker op → tryk **Kvittér** → vent til grøn. Klip ventetiden, hvis den er lang

**Sig:**
> Nu den rigtige Pi. Den står på mit bord og sender sin måling hvert femte sekund over Wi-Fi til min PC.
> Lige nu er den grøn. Jeg puster på sensoren …
> Fugten stiger, LED'en bliver rød, og her i kontrolcentret dukker alarmen op.
> Som medarbejder trykker jeg Kvittér, så kollegerne kan se, at nogen har taget den.
> Når fugten falder under 55 igen, lukker alarmen af sig selv, og LED'en bliver grøn.
> Kortene for lufttryk og rystelser er grå, fordi de er mockups til fase 2.

---

## Scene 9 · Overvågning af driften med Grafana (4:15–4:35)

**Krav:** Rapportens afsnit E (monitorering) · Forløb 4 (observability, incident management)
**Vis:** `localhost:3000`: peg på kurven "Fugt over tid" (toppen fra lige før), "Åbne alarmer", "Sekunder siden seneste måling" og "MTTA (median)"

**Sig:**
> Kontrolcentret er til medarbejderen. Grafana er til driften.
> Det læser direkte fra databasen. Her kan I se toppen fra før, antallet af åbne alarmer, og hvor længe siden Pi'en sidst sendte noget. Hvis det tal bliver ved med at stige, er sensoren død.
> MTTA er tiden fra en alarm åbner, til nogen kvitterer. Det er mål 6 i rapporten, og målet er under et kvarter.

---

## Scene 10 · CI/CD og vejen frem (4:35–5:05)

**Krav:** Afsnit 3 (CI/CD med GitHub Actions) · vurdering: refleksion og videreudvikling
**Vis:** GitHub → Actions → klik på en grøn kørsel, så trinene ses. Slut på diagrammet "Vejen frem" (`docs/img/diagram-simpel-6-vejen-frem.png`)

**Sig:**
> Til sidst CI/CD. Hver gang vi pusher til main, kører GitHub Actions det hele automatisk:
> den scanner for sårbarheder i pakkerne, kører vores fem tests, bygger og starter Docker, kører Postman-samlingen mod løsningen og tjekker, at Grafana er oppe. Det tager omkring et minut.
> Vi har med vilje holdt MVP'en lille. Næste skridt kunne være flere måletyper som tryk og rystelser, login og HTTPS, og at flytte det hele op i Azure.
> Tak fordi I så med.

---

## Kontrol: dækker videoen opgaven?

| Opgavens krav | Scene |
|---|---|
| **Afsnit 4:** Hvordan løsningen køres op lokalt | 3 |
| **Afsnit 4:** Hvor REST API er dokumenteret (GitHub og Swagger) | 4, 5 |
| **Afsnit 4:** Virker via test med Postman | 6 |
| **Afsnit 4:** Data persisteres i database | 7 |
| Afsnit 2: Domæne, core subdomain, forretningsbehov | 1 |
| Afsnit 2: Event-flow (Sensor Value Received → Anomaly Detected) og regellogik | 2, 4, 8 |
| Afsnit 3: REST API tilgået fra remote IoT device | 8 |
| Afsnit 3: Input → behandling → output, validering | 5, 6, 8 |
| Afsnit 3: Separat database | 3, 7 |
| Afsnit 3: Lokal Docker container | 3 |
| Afsnit 3: CI/CD med GitHub Actions + GitHub-repo | 4, 10 |
| Afsnit E / Forløb 4: Monitorering | 9 |
| Afsnit F: Videreudvikling | 10 |

## Hvis noget driller under optagelsen

| Problem | Løsning |
|---|---|
| LED'en er blå | Pi'en kan ikke nå PC'en. Tjek IP med `ipconfig`, og at Docker kører |
| Pust giver ikke over 60 %RH | Pust tæt på og et par gange i træk. Ellers vis det med Postman-kald 2 i stedet |
| Postman kald 4 giver 409 | En gammel alarm fra `postman-01` var allerede åben og kvitteret. Kør samlingen én gang til: kald 5 har lukket den, så alt er grønt |
| Grafana er tom | Vælg "Last 1 hour" øverst til højre, og send et par målinger først |
