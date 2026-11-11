# Diagrammer over den simple fugt-MVP

Alle diagrammer er tegnet ud fra koden i dette repo (Egen fremstilling, 2026). Kilderne (HTML) ligger i projektmappen `rapport/byg/diagrammer-simpel/`.

| Fil | Billedtekst |
|---|---|
| `diagram-simpel-1-arkitektur.png` | Arkitektur: Raspberry Pi med Sense HAT sender målinger over Wi-Fi til FastAPI og PostgreSQL i hver sin Docker-container på laptoppen; kontrolcentret i browseren henter data og kvitterer. |
| `diagram-simpel-2-alarmflow.png` | Reglerne: farveskalaen grøn/gul/rød (55 og 60 %RH) og en alarms liv fra åben over kvitteret til lukket, med hysterese og testene 2–5 på pilene. |
| `diagram-simpel-3-sekvens.png` | Sekvens: hvad der sker trin for trin, når Pi'en måler 63,1 %RH (validering, regler, én databasetransaktion, rød LED), og når en medarbejder kvitterer. |
| `diagram-simpel-4-cicd.png` | CI/CD: GitHub Actions kører pip-audit, de 5 tests, bygger og starter Docker-stakken og kører Postman mod den ved hvert push til main. |
| `diagram-simpel-5-datamodel.png` | Datamodel: tabellerne `measurement` (Sensor Value Received) og `alarm` (Anomaly Detected) med kolonner, typer og betydning. |
| `diagram-simpel-7-context-map.png` | Fra Event Storming til bounded contexts: Event Storming fra delopgave 1 i forenklet form med farveforklaring, de fire contexts (Enhed & Måling, Overvågning & Alarm, Servicesag, Feltservice) med ansvar, sprog og capabilities, og context mappet med relationerne. Rapportens figur 1. |
| `diagram-simpel-8-teknisk-arkitektur.png` | Teknisk arkitektur: sensorer, netværk, REST API (lag), PostgreSQL, CI/CD, event-bus og eksterne systemer (Business Central, Mobile Service App, Salesforce), farvet efter bounded context og nummereret efter arkitekturmønster. Rapportens figur 2. |
| `diagram-simpel-6-vejen-frem.png` | Vejen frem: MVP'en nu, næste skridt og den fulde model (RaspPI-prototypen) for sensorer, regler, Pi, kodestruktur, database, API, sikkerhed, test og CI/CD. |
