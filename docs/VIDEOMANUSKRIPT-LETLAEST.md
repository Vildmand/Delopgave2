# Videomanuskript, letlæst udgave: tal først, film bagefter

Sådan bruger du det:

1. **Del 1: Indtal stemmen.** Læs de 10 afsnit op, ét ad gangen. Gem hvert afsnit som sin egen lydfil (`01.m4a`, `02.m4a` …). Hvis du siger noget forkert, så tag bare afsnittet om.
2. **Del 2: Film skærmen.** Optag de 10 klip fra listen. Hvert klip skal vare mindst lige så længe som lydfilen.
3. **Klip det sammen.** Læg lydfilerne efter hinanden på tidslinjen, og læg klippene ovenpå. Er et klip for langt, så skær i det eller sæt farten op (fx mens Docker starter).
   På Windows kan du bruge **Clipchamp**, som er installeret i forvejen.

Hele speaken er ca. 640 ord. Det giver omkring 4½–5 minutter.

---

# Del 1: Speak (læs op)

### 1. Intro · ca. 30 sek.

Hej. Vi er gruppe 9.

Vi har bygget et teknisk MVP til Intelligent IoT Solutions. Mere præcist til Managed Services, hvor kontrolcentret overvåger kundernes udstyr døgnet rundt.

Problemet er fugt. For høj luftfugtighed kan ødelægge udstyr, og tit opdager man det først, når noget går i stykker.

Derfor måler vi fugten. Når den bliver for høj, får medarbejderen en alarm, før det bliver til et stop.

Her er vores context map fra delopgave 1. MVP'en bygger de to vigtigste dele: "Enhed og måling" og "Overvågning og alarm".

### 2. Arkitektur · ca. 30 sek.

Sådan hænger det sammen.

En Raspberry Pi med en Sense HAT måler fugten. Den sender målingen over Wi-Fi til vores REST API. Det er eventet "Sensor Value Received".

API'et tjekker værdien. Over 60 procent er rødt, og så åbner vi en alarm. Det er eventet "Anomaly Detected".

Alarmen dukker op i kontrolcentret, og lyset på Pi'en bliver rødt.

Alt bliver gemt i en PostgreSQL-database, der kører for sig selv.

### 3. Kør det op · ca. 20 sek.

For at prøve løsningen skal man kun have Docker.

Man henter koden fra GitHub og skriver én kommando: docker compose up.

Så starter tre containere: databasen, vores API og Grafana.

Databasen er ikke åben udadtil. Det er kun API'et, der kan tale med den.

### 4. Koden · ca. 25 sek.

Her er koden på GitHub. Vi har holdt serveren lille: tre Python-filer.

Reglen ligger i filen rules.py. Over 60 er rødt. Mellem 55 og 60 er gult. Under 55 er grønt.

Alarmen lukker først igen under 55. Ellers ville den blinke til og fra, når fugten ligger omkring 60.

Al koden har danske kommentarer, og der er en kodeguide, der forklarer hver fil.

### 5. Dokumentation af API'et · ca. 30 sek.

API'et er dokumenteret to steder. I README-filen på GitHub, og i Swagger, som laves automatisk ud fra koden.

Der er fire endpoints. Man kan sende en måling, hente målinger, hente alarmer og kvittere for en alarm.

Lad os prøve at sende noget forkert: en fugt på 150 procent.

API'et svarer med fejl 422 og forklarer hvorfor. Kun 0 til 100 er gyldigt. Den forkerte måling bliver aldrig gemt.

### 6. Test med Postman · ca. 30 sek.

Nu tester vi hele forløbet i Postman. Der er fem kald, som følger en alarm fra start til slut.

Først en normal måling. Den giver grøn.

Så en høj måling på 62. Den giver rød og åbner en alarm.

Vi henter alarmen og kvitterer for den.

Til sidst en normal måling, som lukker alarmen igen.

Alle fem tests er grønne.

### 7. Data i databasen · ca. 25 sek.

Er det så også gemt? Vi kigger direkte i databasen.

Her er målingerne, hver med den farve, serveren har givet dem.

Og her er alarmen. Den har tre tidspunkter: hvornår den blev åbnet, hvornår den blev kvitteret, og hvornår den blev lukket.

Dem bruger vi til at måle, hvor hurtigt kontrolcentret reagerer.

### 8. Den rigtige Pi · ca. 40 sek.

Nu den rigtige Pi. Den sender en måling hvert femte sekund over Wi-Fi til min computer.

Lige nu lyser den grønt.

Jeg puster på sensoren. Fugten stiger, lyset bliver rødt, og alarmen dukker op i kontrolcentret.

Som medarbejder trykker jeg "Kvittér". Så kan kollegerne se, at nogen har taget sig af den.

Når fugten falder under 55 igen, lukker alarmen af sig selv, og lyset bliver grønt.

Kortene for lufttryk og rystelser er grå. Det er skitser til fase 2.

### 9. Grafana · ca. 25 sek.

Kontrolcentret er til medarbejderen. Grafana er til driften.

Grafana læser direkte fra databasen. Her ser I toppen fra før, hvor mange alarmer der er åbne, og hvor længe siden Pi'en sidst sendte noget. Bliver det tal ved med at stige, er sensoren gået ned.

MTTA er tiden, fra en alarm åbner, til nogen kvitterer. Vores mål er under et kvarter.

### 10. CI/CD og afslutning · ca. 30 sek.

Til sidst CI/CD.

Hver gang vi lægger ny kode på GitHub, kører alt automatisk. Den tjekker pakkerne for sikkerhedshuller, kører vores fem tests, starter løsningen i Docker, kører Postman og tjekker, at Grafana virker. Det tager omkring et minut.

Vi har med vilje holdt MVP'en lille. Næste skridt kunne være flere målinger som tryk og rystelser, login og kryptering, og at flytte det hele op i Azure.

Tak fordi I så med.

---

# Del 2: Skærmoptagelser (film bagefter)

**Gør klar først:** Start Docker (`docker compose up --build`), og start Pi'en med `API_URL=http://<pc-ip>:8000 python3 pi.py`.
Zoom browseren til 125 %, og slå notifikationer fra.
Optag klip 8 (Pi'en) **før** klip 9 (Grafana), så toppen fra pustet kan ses i Grafana.

| Klip | Varighed | Hvad du filmer |
|---|---|---|
| **1** | 30 sek. | Rapportens figur 1 i bilag E (context map). Rul langsomt eller zoom ind på de to contexts, MVP'en bygger |
| **2** | 30 sek. | Rapportens figur 2 i bilag E (arkitektur). Før musen fra Pi → API → database → kontrolcenter i takt med speaken |
| **3** | 20 sek. | Terminal: skriv `docker compose up --build`. Skru farten op, mens den starter. Skriv `docker compose ps`, så de tre containere ses |
| **4** | 25 sek. | GitHub: repoets forside med filerne. Klik på `rules.py`, og hold på reglerne (55 og 60) |
| **5** | 30 sek. | Rul kort til API-tabellen i README. Åbn `localhost:8000/docs`. Klik **POST /measurements** → *Try it out* → skriv `150` ved humidity → *Execute* → vis svaret 422 |
| **6** | 30 sek. | Postman: vis de fem kald. Tryk **Run collection** → vis at alle er grønne |
| **7** | 25 sek. | Terminal: `docker compose exec db psql -U fugt -c "select * from measurement order by id desc limit 5;" -c "select * from alarm order by id desc limit 3;"` |
| **8** | 40 sek. | Film Pi'en med telefonen, og optag kontrolcentret (`localhost:8000`) på skærmen samtidig. Pust → rødt lys → alarm → tryk **Kvittér** → vent til grønt. Skær ventetiden væk. Slut på de grå kort for tryk og rystelser |
| **9** | 25 sek. | `localhost:3000`: peg på "Fugt over tid", "Åbne alarmer", "Sekunder siden seneste måling" og "MTTA (median)" |
| **10** | 30 sek. | GitHub → **Actions** → en grøn kørsel, så trinene ses. Slut på billedet `docs/img/diagram-simpel-6-vejen-frem.png` |

**Hvis noget driller:**
Blåt lys på Pi'en betyder, at den ikke kan nå computeren (tjek IP med `ipconfig`).
Kommer fugten ikke over 60, så pust tættere på et par gange i træk.
Giver Postman fejl 409, så kør samlingen én gang til.

Den fulde udgave med krav til hver scene: `docs/VIDEOMANUSKRIPT.md`.
