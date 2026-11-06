# Videomanuskript (ca. 5 minutter)

Opgaven kræver at vise: hvordan løsningen køres op, hvor API'et er dokumenteret, test med Postman, og at data gemmes i databasen.

| Tid | Skærm | Sig |
|---|---|---|
| 0:00–0:30 | Arkitekturdiagrammet (rapportens figur 1) | "Vi overvåger luftfugtighed for IIS Managed Services. Pi'en måler, serveren afgør grøn, gul eller rød, og over 60 % åbnes en alarm, som en medarbejder kvitterer for. Eventet Sensor Value Received bliver til Anomaly Detected." |
| 0:30–1:15 | GitHub-repoet: filerne og `rules.py` | "Hele serveren er tre filer. Reglen ligger i rules.py: over 60 rød, under 55 grøn igen. Mellemrummet er hysterese, så alarmen ikke blinker." |
| 1:15–1:45 | Terminal: `docker compose up --build` | "Vi kører lokalt i Docker. To containere: PostgreSQL som separat database, og vores API." |
| 1:45–2:15 | Browser: `localhost:8000/docs` | "API'et er dokumenteret i Swagger, som FastAPI laver automatisk, og i README på GitHub. Fire endpoints." |
| 2:15–3:15 | Postman: Run collection | "Postman kører hele flowet: normal måling, høj måling åbner en alarm, vi henter den, kvitterer og sender en normal måling, der lukker den. Alle fem tests er grønne." |
| 3:15–3:45 | Terminal: `docker compose exec db psql -U fugt -c "select * from measurement;" -c "select * from alarm;"` | "Data er gemt i PostgreSQL. Her er målingerne, og her alarmen med tidspunkt for åbnet, kvitteret og lukket." |
| 3:45–4:30 | Pi'en + kontrolcentret side om side | "Nu den rigtige Pi. Jeg puster på sensoren: LED'en bliver rød, alarmen dukker op i kontrolcentret, jeg trykker Kvittér. Når fugten falder under 55, lukkes den. Lufttryk og rystelser er grå mockups til fase 2." |
| 4:30–5:00 | GitHub Actions: grøn kørsel | "CI/CD på GitHub Actions: sårbarhedsscan, de fem tests, Docker-build og Postman mod den kørende løsning. Den store udgave ligger i vores første repo og viser vejen frem." |
