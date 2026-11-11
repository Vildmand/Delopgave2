# Videomanuskript (ca. 5 minutter)

Opgaven kræver at vise: hvordan løsningen køres op, hvor API'et er dokumenteret, test med Postman, og at data gemmes i databasen.

| Tid | Skærm | Sig |
|---|---|---|
| 0:00–0:40 | Rapportens figur 1 (context map), derefter figur 2 (teknisk arkitektur) | "Vi overvåger luftfugtighed for IIS Managed Services, værdistrømmen VS7. Fra vores Event Storming i delopgave 1 har vi lavet fire bounded contexts. MVP'en bygger de to core contexts: Enhed og Måling, og Overvågning og Alarm. Her er den tekniske arkitektur: Pi'en sender over Wi-Fi til et REST API med egen PostgreSQL. Event-bussen og Business Central er næste skridt. Pi'en måler, serveren afgør grøn, gul eller rød, og over 60 % åbnes en alarm. Sensor Value Received bliver til Anomaly Detected." |
| 0:40–1:15 | GitHub-repoet: filerne, `rules.py` og diagrammet over alarmflowet (`docs/img/diagram-simpel-2-alarmflow.png`) | "Hele serveren er tre filer, og al koden har danske kommentarer. Reglen ligger i rules.py: over 60 rød, under 55 grøn igen. Mellemrummet er hysterese, så alarmen ikke blinker. Kodeguiden i docs forklarer hver fil, og hvorfor den er skrevet sådan." |
| 1:15–1:45 | Terminal: `docker compose up --build` | "Vi kører lokalt i Docker. To containere: PostgreSQL som separat database, og vores API." |
| 1:45–2:15 | Browser: `localhost:8000/docs` | "API'et er dokumenteret i Swagger, som FastAPI laver automatisk, og i README på GitHub. Fire endpoints." |
| 2:15–3:15 | Postman: Run collection | "Postman kører hele flowet: normal måling, høj måling åbner en alarm, vi henter den, kvitterer og sender en normal måling, der lukker den. Alle fem tests er grønne." |
| 3:15–3:45 | Terminal: `docker compose exec db psql -U fugt -c "select * from measurement;" -c "select * from alarm;"` | "Data er gemt i PostgreSQL. Her er målingerne, og her alarmen med tidspunkt for åbnet, kvitteret og lukket." |
| 3:45–4:30 | Pi'en + kontrolcentret side om side | "Nu den rigtige Pi. Jeg puster på sensoren: LED'en bliver rød, alarmen dukker op i kontrolcentret, jeg trykker Kvittér. Når fugten falder under 55, lukkes den. Lufttryk og rystelser er grå mockups til fase 2." |
| 4:30–5:00 | GitHub Actions: grøn kørsel, derefter diagrammet "Vejen frem" (`docs/img/diagram-simpel-6-vejen-frem.png`) | "CI/CD kører automatisk ved hvert push til main: sårbarhedsscan, de fem tests, Docker-build og Postman mod den kørende løsning, på under et minut. Den store udgave ligger i vores første repo, og diagrammet viser, hvordan vi ville bygge videre: robust regel, hændelseslog, flere måletyper, lag og migrationer, kø på Pi'en og til sidst login, HTTPS og Azure." |
