---
forside_titel: "Delopgave 2 – Fra sensor til alarm (simpel MVP, letlæst udgave)"
forside_felter:
  - ["Uddannelsesinstitutionens navn:", "Erhvervsakademi København"]
  - ["Uddannelsens navn:", "Økonomi & IT"]
  - ["Projektbetegnelse:", "Teknisk MVP (Minimum Viable Product: den mindste udgave af et produkt, der virker) – en REST API microservice (en lille, selvstændig webtjeneste, som andre programmer kan sende og hente data fra). Faget 6.2 Design og implementering af digitale løsninger"]
  - ["Navn:", "Brian Jegindø|[mail]|Mie Mosberg|mimo0006@stud.ek.dk|Nicklas Vilmann|nivi0001@stud.ek.dk|Rene Dalby|rehe0001@stud.ek.dk|Tobias Stryhn|tost0003@stud.ek.dk"]
  - ["Gruppe:", "Gruppe 9"]
  - ["Semester:", "6. semester"]
  - ["Vejledere:", "[vejledere]"]
  - ["Repository (kodens placering på GitHub):", "https://github.com/Vildmand/Delopgave2"]
  - ["Video:", "[link]"]
  - ["Antal sider:", "se PDF"]
lang: da-DK
---

# Fra sensor til alarm: Fugtovervågning hos IIS {.unnumbered .del}

## 1. Problem og domæne

I delopgave 1 analyserede vi virksomheden Intelligent IoT Solutions A/S, som vi i resten af rapporten kalder IIS. IoT står for Internet of Things (på dansk "tingenes internet") og betyder, at fysiske ting som sensorer og maskiner er koblet på internettet og sender data. IIS laver sensorer til blandt andet vindmølleindustrien og har et nyt forretningsområde, der hedder *Managed Services*. Her overvåger IIS mod betaling kundernes anlæg døgnet rundt fra et kontrolcenter i Aalborg. Området forventes at stå for mindst 10 % af omsætningen inden for fem år (Casebeskrivelse, 2026).

Vores analyse i delopgave 1 pegede på én bestemt værdistrøm. En værdistrøm er rækken af trin, en kunde går igennem for at få et bestemt resultat. Den hedder VS7 (værdistrøm nummer 7 i delopgave 1): *Få anlæg overvåget og vedligeholdt proaktivt*. Proaktivt betyder, at man handler, før noget går galt, i stedet for at vente på, at kunden ringer. I delopgave 1 kaldte vi Managed Services et kerneområde, fordi det er her, IIS skiller sig ud fra konkurrenterne (Delopgave 1, 2026).

Opgaven beder os om at bygge scenariet *Predictive Maintenance / notifikation* (på dansk forudsigende vedligeholdelse og besked). Scenariet har to hændelser: *Sensor Value Received* (en måling er modtaget) og *Anomaly Detected* (en afvigelse er opdaget). Beslutningen er et tjek mod en grænse, og handlingen er en alarm (Erhvervsakademi København, 2026).

Vi har bygget det mindste, der viser hele kæden. Man kan sammenligne løsningen med en røgalarm. En Raspberry Pi (en billig computer på størrelse med et kreditkort, som vi i resten af rapporten kalder Pi'en) har et påsat sensorkort, der hedder Sense HAT (HAT står for Hardware Attached on Top, altså et ekstra kort, der sættes oven på Pi'en). Pi'en måler luftfugtigheden og sender den til vores server. Serveren vurderer målingen og opretter en alarm, hvis fugten er for høj. En medarbejder ser alarmen på en hjemmeside og kvitterer for den. Alt bliver gemt i en database. For IIS' kunder er behovet færre uventede stop, fordi fugt i for eksempel et styreskab i en vindmølle kan give rust og kortslutning, længe før noget går i stykker.

Rapportens problemstilling er derfor: *Hvordan kan IIS med en lille, selvstændig webtjeneste gøre målinger fra sensorer til alarmer, som medarbejderne kan handle på i tide, og hvordan kan løsningen bygges, testes og startes automatisk?*

### 1.1. Centrale begreber og forkortelser

Rapporten bruger en del fagord. De vigtigste er forklaret i tabel 1. Forkortelser bliver desuden forklaret i en parentes, første gang de bruges i teksten.

| Begreb | Forklaring |
|-------|-----------------|
| API (Application Programming Interface) | En fast indgang til et program. Andre programmer kan sende og hente data gennem den, ligesom man bestiller ved en skranke i stedet for selv at gå ud i køkkenet. |
| REST (Representational State Transfer) | En udbredt måde at bygge et API på, hvor man bruger internettets almindelige kommandoer som GET ("hent") og POST ("send") (Fielding, 2000). |
| Endpoint | Én bestemt adresse i API'et, for eksempel `/measurements`, hvor man kan sende eller hente én slags data. |
| MVP (Minimum Viable Product) | Den mindste udgave af et produkt, der virker og kan afprøves, så man lærer så tidligt som muligt (Ries, 2011). |
| Microservice | En lille, selvstændig webtjeneste, der løser én opgave og kan startes og ændres uden at røre resten af systemet. |
| Server og database | Serveren er det program, der modtager målingerne og træffer beslutningerne. Databasen er et særskilt program, der gemmer data sikkert og ordnet, ligesom et stort arkivskab. |
| Hændelse (på engelsk event) | En besked om noget, der allerede er sket, for eksempel "måling modtaget" eller "alarm oprettet". |
| %RH (relativ luftfugtighed) | Hvor meget vand luften indeholder, i procent af hvad den højst kan indeholde. Almindelig indeluft ligger på 30–50 %. |
| Hysterese | Alarmen starter over 60 %RH, men slukker først under 55 %RH. Så blinker den ikke frem og tilbage, hvis fugten vipper omkring 60. Det svarer til en termostat, der ikke tænder og slukker hvert sekund. |
| Docker og container | Docker er et program, der pakker software i containere. En container er en lukket kasse med programmet og alt, hvad det skal bruge, så det kører ens på alle computere. |
| DevSecOps (Development, Security, Operations) | En arbejdsform, hvor udvikling, sikkerhed og drift hænger sammen i én automatisk proces, så sikkerheden er med fra starten. |
| CI/CD (Continuous Integration / Continuous Delivery) | Løbende og automatisk kontrol, hvor koden bliver testet, bygget og startet, hver gang den ændres. |

::: {custom-style="Billedtekst"}
(Tabel 1, egen fremstilling (2026): Begreber og forkortelser)
:::

### 1.2. Afgrænsning

Vi har bevidst bygget så lidt som muligt. Kun luftfugtighed bliver målt rigtigt. Lufttryk og rystelser vises som grå kort med teksten *Fase 2 – mockup* (en mockup er en attrap, der viser, hvordan noget kommer til at se ud) og faste eksempeltal, så man kan se, hvordan løsningen kan vokse. Grænserne er valgt for at kunne vise løsningen frem og ikke for at passe til en bestemt maskine. Løsningen opdager afvigelser, når de sker, men den forudsiger ikke, hvornår noget går i stykker. Vi byggede først en langt større udgave, men skar den ned, så hver linje kode kan forklares og føres tilbage til opgavens krav. Den store udgave beskriver vi i refleksionen (afsnit 6.3).

## 2. Løsningsdesign

### 2.1. Overordnet arkitektur

Arkitektur betyder her, hvilke dele løsningen består af, og hvordan de taler sammen. Løsningen kører i Docker på en almindelig bærbar computer. Databasen kører i sin egen container ved siden af serveren, som opgaven kræver. Pi'en, testprogrammet Postman (et program til at sende testforespørgsler til et API) og kontrolcentret taler alle med serveren gennem det samme API. Det er kun serveren, der bestemmer, om en måling er normal, og om der skal være en alarm (se figur 1). De andre viser bare, hvad serveren har besluttet.

![](img/diagram-simpel-1-arkitektur.png){width=100%}

::: {custom-style="Billedtekst"}
(Figur 1, egen fremstilling (2026): Løsningens opbygning. Pi'en sender målinger over Wi-Fi til serveren og databasen, som kører i hver sin Docker-container på den bærbare computer. Kontrolcentret i browseren henter data og kvitterer. Nederst ses den automatiske kontrol på GitHub)
:::

### 2.2. Event-flowet: hændelse, beslutning og handling

Opgaven kræver mindst ét event-flow (et forløb, der starter med en hændelse) og mindst én regel. Vores forløb ser sådan ud:

1. **Hændelse:** Pi'en sender en måling, for eksempel 62,0 %RH, til adressen `/measurements`. Det er *Sensor Value Received*. Målingen bliver gemt.
2. **Beslutning:** Reglen siger grøn under 55 %RH, gul fra 55 til 60 %RH og rød over 60 %RH.
3. **Handling:** Hvis målingen er rød, og der ikke allerede er en alarm, oprettes en alarm. Det er *Anomaly Detected*. Svaret til Pi'en fortæller, at lysdisplayet skal lyse rødt.
4. **Afslutning:** En medarbejder kvitterer for alarmen i kontrolcentret, som betyder "jeg har set den". Alarmen lukker af sig selv, når fugten er under 55 %RH igen.

Figur 2 viser reglerne og en alarms liv fra den bliver oprettet, over kvitteringen, til den er normal igen.

![](img/diagram-simpel-2-alarmflow.png){width=100%}

::: {custom-style="Billedtekst"}
(Figur 2, egen fremstilling (2026): Øverst farveskalaen med grænserne 55 og 60 %RH. Nederst en alarms forløb. Numrene på pilene er de tests, der kontrollerer hvert skridt)
:::

Tabel 2 viser, hvordan analysen i delopgave 1 er blevet til regler i koden og til tests. Hver regel har præcis én test, så man kan se, at den virker.

| Fra delopgave 1 (strategi) | Regel i koden | Test |
|---|---|---|
| Evnen til at følge hver enheds tilstand | Grøn under 55, gul 55–60, rød over 60 | 1. farverne |
| Event Storming: "Fejl rapporteret" → "Generer alert" | En rød måling opretter en alarm | 2. alarm over 60 |
| Medarbejderne må ikke drukne i alarmer | Ingen ny alarm, mens der allerede er en | 3. ingen dobbelte alarmer |
| Medarbejderen tager ansvar for alarmen | Kvittering | 4. kvittering |
| Alarmen må ikke blinke ved grænsen | Lukker først under 55 (hysterese) | 5. normalisering |

::: {custom-style="Billedtekst"}
(Tabel 2, egen fremstilling (2026): Fra strategi til regel til test)
:::

Event Storming er en workshopmetode, hvor man med post-it-sedler sætter alle hændelser i en forretningsproces op på en tidslinje (Brandolini, 2013). Vi brugte den i delopgave 1, og den fandt kæden "Fejl rapporteret" → "Generer alert" → "ALERT genereret". Det er præcis den kæde, løsningen nu udfører (Delopgave 1, 2026).

## 3. Implementering

### 3.1. Sådan er løsningen bygget op

Løsningen er skrevet i programmeringssproget Python med værktøjet FastAPI, som er et Python-værktøj til hurtigt at bygge et API. FastAPI laver også automatisk en vejledning til API'et, som hedder Swagger. Data gemmes i PostgreSQL, som er en gratis og meget udbredt database. Vi bruger Python både på Pi'en og på serveren, fordi det gør koden lettere at forklare. Hele løsningen består af fem små filer (se tabel 3).

| Fil | Opgave | Linjer |
|---|---|---|
| `main.py` | API'et med fire endpoints: send måling, hent målinger, hent alarmer og kvittér | ca. 140 |
| `rules.py` | Reglerne som tre små funktioner, der ikke kender databasen (se figur 3) | ca. 45 |
| `db.py` | Databasens to tabeller: `measurement` (måling) og `alarm` | ca. 65 |
| `static/index.html` | Kontrolcentret: fugten lige nu, alarmer med en Kvittér-knap og de grå mockup-kort | ca. 135 |
| `pi/pi.py` | Programmet på Pi'en: læs fugten, send den og farv lysdisplayet | ca. 50 |

::: {custom-style="Billedtekst"}
(Tabel 3, egen fremstilling (2026): Kodens filer. Linjetallet tæller de forklarende danske kommentarer med, som står i al koden)
:::

Reglerne er hjertet i løsningen (se figur 3). De ligger i deres egen fil og kender hverken databasen, netværket eller Pi'en. **Hvorfor:** Så kan de testes på en brøkdel af et sekund, og hvis IIS vil ændre grænserne, skal det kun ske ét sted. Grænserne 55 og 60 står øverst som faste værdier, så man ikke skal lede efter dem. Betingelsen `and not alarm_already_open` sørger for, at ti røde målinger i træk kun giver én alarm.

![](img/01-rules.png){width=68%}

::: {custom-style="Billedtekst"}
(Figur 3, egen fremstilling (2026): Reglerne i rules.py med de rigtige linjenumre. Koden er på engelsk, kommentarerne på dansk)
:::

### 3.2. API'et

Programmer taler med serveren ved at sende forespørgsler over HTTP (Hypertext Transfer Protocol, som er det samme "sprog", en browser bruger til at hente hjemmesider). Tabel 4 viser de fire endpoints.

| Hvad man gør | Adresse | Hvem bruger det |
|-------|-----|-----|
| Sende en ny måling, som serveren vurderer med det samme | POST `/measurements` | Pi'en og Postman |
| Se de seneste målinger | GET `/measurements` | Kontrolcentret |
| Se de seneste alarmer | GET `/alarms` | Kontrolcentret og Postman |
| Kvittere for en alarm | POST `/alarms/{id}/ack` | Kontrolcentret og Postman |

::: {custom-style="Billedtekst"}
(Tabel 4, egen fremstilling (2026): API'ets fire endpoints)
:::

API'et er dokumenteret to steder: i Swagger, som man åbner i en browser på adressen `/docs` og kan prøve API'et af direkte fra, og i en tabel i projektets README-fil på GitHub (en README er projektets "læs mig først"-side).

Figur 4 viser hele event-flowet i koden. De tre trin hændelse, beslutning og handling står som tre kommentarer. **Hvorfor:** Endpointet spørger reglerne i stedet for selv at sammenligne tal, så forretningsreglerne kun ligger ét sted. Før koden overhovedet kører, tjekker værktøjet Pydantic (et Python-værktøj, der kontrollerer data), at fugten er et tal mellem 0 og 100 (se bilag A, kodeuddrag 2).

![](img/03-post-measurements.png){width=82%}

::: {custom-style="Billedtekst"}
(Figur 4, egen fremstilling (2026): Endpointet POST /measurements, hvor en måling bliver til en farve og måske en alarm)
:::

### 3.3. Sådan gemmes data

Databasen har to tabeller. En tabel er ligesom et regneark med rækker og kolonner. Begge hændelser fra opgaven bliver gemt:

- Hver række i tabellen `measurement` er en *Sensor Value Received* med enhedens navn, fugten, farven og tidspunktet.
- Hver række i tabellen `alarm` er en *Anomaly Detected*. Den har tre tidspunkter, der fortæller hele forløbet: hvornår alarmen blev oprettet, hvornår den blev kvitteret, og hvornår den blev normal igen.

Målingen og en eventuel alarm bliver gemt i én samlet arbejdspakke, en såkaldt transaktion (linje 102 i figur 4). Enten bliver alt gemt, eller også bliver intet gemt, så der aldrig kun bliver gemt halvdelen. Tabellerne kan ses i bilag A, kodeuddrag 5, og som tegning i bilag B.

Data bliver tjekket, før de bruges. Fugten skal ligge mellem 0 og 100 %RH. Ellers svarer API'et med fejlkode 422 (som betyder "forkerte data") og gemmer ingenting. Prøver man at kvittere for en alarm, der ikke findes, svarer API'et med fejlkode 404 ("findes ikke"), og kvitterer man to gange, svarer det med fejlkode 409 ("allerede gjort").

### 3.4. Pi'en og kontrolcentret

Pi'en måler hvert 5. sekund og sender målingen til den bærbare computers adresse på det lokale netværk (`http://192.168.0.103:8000`). Det viser, at API'et kan nås fra en anden computer, som opgaven kræver. Pi'en har et lysdisplay med 64 små LED-lamper (LED står for Light Emitting Diode, på dansk en lysdiode). Hele displayet lyser grønt, gult eller rødt efter serverens svar og blåt, hvis serveren ikke kan nås (se bilag A, kodeuddrag 6). Pi'en regner ikke selv. Reglerne ligger kun på serveren, så de kan ændres ét sted.

Kontrolcentret er en hjemmeside, som serveren selv leverer. Den henter nye data hvert 3. sekund og viser fugten lige nu, en tabel med alarmer og en Kvittér-knap (se figur 5).

![](img/kontrolcenter.png){width=62%}

::: {custom-style="Billedtekst"}
(Figur 5, egen fremstilling (2026): Kontrolcentret med en aktiv alarm, en alarm der er normal igen, og de grå mockup-kort til fase 2)
:::

## 4. DevSecOps og deployment

### 4.1. Sådan bliver løsningen bygget og startet

Deployment betyder at få løsningen i gang på den computer, hvor den skal køre. Vores løsning kører lokalt i Docker og startes med én kommando: `docker compose up --build`. Kommandoen bygger vores kode og starter to containere: `db` med PostgreSQL og `api` med vores server. Serveren venter, til databasen er klar, før den starter. Data ligger i et Docker-volume (et lager uden for containeren), så de bliver gemt, selvom man genstarter. Vi har afprøvet det på en bærbar computer med Windows og Docker Desktop.

### 4.2. Automatisk kontrol med GitHub Actions

Vores kode ligger på GitHub, som er en hjemmeside, hvor programmører gemmer og deler kode. GitHub Actions er GitHubs tjeneste til automatiske kørsler. Hver gang vi sender ny kode til hovedgrenen (på engelsk main, den officielle udgave af koden), kører GitHub Actions de fire trin i tabel 5 af sig selv. Hvis ét trin fejler, stopper kørslen, og fejlen kan ses på GitHub. Opskriften ligger i filen `.github/workflows/ci.yml` (se bilag A, kodeuddrag 11, og tegningen i bilag B).

| Trin | Hvad sker der (værktøjets navn) |
|---|---|
| 1. Sikkerhed | De færdige pakker, vi bruger, bliver tjekket for kendte sikkerhedshuller (pip-audit) |
| 2. Test | De 5 automatiske tests bliver kørt (pytest) |
| 3. Byg og start | Containeren bliver bygget, og hele løsningen med server og PostgreSQL bliver startet på GitHubs computer |
| 4. Test af hele kæden | Postman-testene bliver kørt mod den kørende løsning, ligesom en rigtig bruger ville gøre (Newman, som er Postman til automatiske kørsler) |

::: {custom-style="Billedtekst"}
(Tabel 5, egen fremstilling (2026): Trinene i den automatiske kontrol)
:::

Den første automatiske kørsel (kørsel nummer 3, den 6. november 2026) var grøn i alle trin og tog under et minut (se figur 6). Den kan ses på https://github.com/Vildmand/Delopgave2/actions/runs/42223918668.

![](img/ci-groen-koersel-3.png){width=58%}

::: {custom-style="Billedtekst"}
(Figur 6, egen fremstilling (2026): Den grønne kørsel nummer 3 på GitHub Actions. Trinene og tiderne er gengivet fra kørslens egne data på GitHub)
:::

CI-delen (den automatiske kontrol) er fuldt automatisk. CD-delen (den automatiske udrulning) kører også automatisk, men kun på GitHubs computer, hvor hele løsningen bliver startet og testet. Selve den bærbare computer, som Pi'en sender til, opdaterer vi med kommandoen ovenfor. Vi har bevidst kun skrevet, at noget er automatisk, hvis det faktisk kører automatisk.

### 4.3. Sikkerhed

Sikkerheden er enkel, men med fra starten, som vi anbefalede i delopgave 1. Containeren kører ikke som administrator (på engelsk root), så et angreb på serveren ikke får fuld adgang. Den automatiske kontrol har kun lov til at læse koden og ikke ændre den. Pakkerne bliver scannet for sikkerhedshuller ved hver ændring. Databasens adgangskode er kun beregnet til en lokal demonstration og skal skiftes ud, før løsningen bruges rigtigt.

## 5. Kvalitet og drift

**Test.** De 5 automatiske tests svarer til de 5 regler i tabel 2. De bruger en tom database i computerens hukommelse og kører på under et sekund. Postman-samlingen gennemspiller hele forløbet i 5 trin: en normal måling, en høj måling, der opretter en alarm, hent alarmen, kvittér for den og en normal måling, der lukker den. Alle 5 tests og alle 5 Postman-trin bestod både på den bærbare computer og på GitHub. Bagefter så vi rækkerne i PostgreSQL med psql, som er PostgreSQL's eget program, hvor man skriver spørgsmål direkte til databasen.

**Afprøvning med rigtigt udstyr.** Programmet er også afprøvet på den rigtige Pi. Den sendte målinger til den bærbare computer over Wi-Fi, og i et tørt lokale på cirka 28 %RH lyste displayet grønt. Når man puster på sensoren, stiger fugten over 60 %RH, displayet bliver rødt, og alarmen dukker op i kontrolcentret.

**Overvågning (monitorering).** Kontrolcentret viser tidspunktet for den seneste måling, så en medarbejder kan se, hvis Pi'en er holdt op med at sende. Pi'en viser blåt, hvis den ikke kan nå serveren. Docker holder øje med, om databasen svarer, før serveren startes.

**Fejlhåndtering.** Forkerte data bliver afvist med en fejlkode, og intet bliver gemt halvt. Hvis netværket fejler, prøver Pi'en bare igen 5 sekunder senere.

**Logning.** En log er en slags dagbog over, hvad programmet gør. Serveren skriver hver forespørgsel i Docker-loggen, som man kan se med `docker compose logs api`. Hvis den automatiske kontrol fejler, viser den selv loggen. Databasen er desuden i sig selv en logbog over alle målinger og alarmer.

## 6. Refleksion

### 6.1. Hvad fungerede godt

Det, der fungerede bedst, var at lade delopgave 1 styre koden. Hver regel kan føres tilbage til strategien, og hver regel har én test (tabel 2). Da kæden "Fejl rapporteret" → "Generer alert" fra Event Storming blev til "alarm oprettet" i koden, databasen og testene, blev det let at forklare løsningen og at se, om den gjorde det rigtige. At holde reglerne i én lille fil uden database gjorde dem lette at teste.

Det fungerede også godt at skære ned. Vi byggede først en stor udgave med tre måletyper, en logbog over hændelser og 153 tests. Den virkede, men den var svær at forklare på få minutter. Ved at skære ned til fem filer fik vi en løsning, hvor man kan følge hele kæden fra måling til kvittering, og hvor alle opgavens krav stadig er opfyldt.

### 6.2. Hvad kunne forbedres

Vi burde have startet småt og bygget ud, i stedet for at bygge stort og skære ned bagefter. Reglen er også meget simpel. Én høj måling giver straks en alarm, så et kort pust eller en åben dør kan give en falsk alarm. Der er ikke noget login, så alle på netværket kan sende målinger og kvittere for alarmer. Forbindelsen mellem Pi'en og serveren er ikke krypteret. Og løsningen er ikke rigtig forudsigende vedligeholdelse. En fast grænse opdager et problem, der sker nu, men forudsiger ikke et problem, der kommer senere. Det er derfor mere præcist at kalde den afvigelsesdetektion, som gør vedligeholdelsen proaktiv.

### 6.3. Hvordan løsningen kan videreudvikles

Den store udgave ligger urørt i vores første repository (https://github.com/miemosberg2201/RaspPI). Den viser, at hvert af de næste skridt kan lade sig gøre, fordi vi allerede har bygget og testet dem. Figur 7 viser, hvordan vi ville komme fra den simple MVP til den store udgave område for område.

![](img/diagram-simpel-6-vejen-frem.png){width=100%}

::: {custom-style="Billedtekst"}
(Figur 7, egen fremstilling (2026): Vejen frem fra MVP'en nu over de næste skridt til den fulde model, som allerede er afprøvet i det første repository)
:::

Vi ville bygge videre i denne rækkefølge, hvor hvert trin kan afprøves for sig, og hvor det vigtigste for forretningen kommer først:

1. **En mere robust regel.** Alarmen skal først starte efter tre høje målinger i træk og først slutte efter tre normale målinger i træk. Det fjerner falske alarmer fra et kort udsving. Hvis der ikke er kommet en måling i 35 sekunder, skal målingen markeres som forældet, så skærmen ikke viser en gammel farve, som om den stadig gælder.
2. **En logbog over hændelser.** En ekstra tabel, hvor alle hændelser bliver gemt og aldrig kan ændres eller slettes bagefter. Så kan andre systemer, for eksempel en service desk (den afdeling, der opretter sager til serviceteknikerne), læse hændelserne uden at ændre reglerne. Det er første skridt mod det fælles beskedsystem (på engelsk en event-bus), som vi foreslog i delopgave 1.
3. **Flere måletyper.** Lufttryk og rystelser med hver deres grænser, men den samme regel. De grå mockup-kort bliver så til rigtige kort. I den store udgave krævede en ny måletype kun nye indstillinger og ikke ny logik.
4. **Kode i lag og styrede databaseændringer.** Koden deles op i fire lag: ét, der tager imod forespørgsler, ét, der styrer forløbet, ét med reglerne og ét, der taler med databasen. Databasen ændres med migrationer (små opskrifter, der ændrer databasen trin for trin uden at miste data). Det gør det sikkert at ændre løsningen, når den bliver større.
5. **En robust Pi.** En kø på Pi'en (på engelsk en outbox), hvor målinger bliver gemt, mens netværket er nede, og sendt bagefter. Så går ingen målinger tabt.
6. **Sikkerhed og drift.** En nøgle til hver enhed og et login til hver medarbejder, så man kan se, hvem der har kvitteret. Krypteret forbindelse med HTTPS (den sikre udgave af HTTP, som også bruges af netbanker). Flere sikkerhedsscanninger i den automatiske kontrol, for eksempel efter adgangskoder, der ved en fejl er kommet med i koden (gitleaks), og efter huller i containeren (Trivy). Til sidst automatisk udrulning til Azure, som er Microsofts tjeneste, hvor man lejer computere over internettet, så en ny udgave kommer i gang af sig selv, når den er godkendt.

Pointen med MVP'en er, at vi nu kan tage trinene ét ad gangen, når der er et behov i forretningen for dem, i stedet for at bygge det hele på én gang. Det passer med delopgave 1, hvor vi skrev, at teknologi skal vælges, fordi den løser et behov, og ikke for teknologiens egen skyld (Delopgave 1, 2026).

## Litteraturliste {.unnumbered}

Brandolini, A. (2013). *Introducing EventStorming*. Leanpub.

Casebeskrivelse (2026). *Intelligent IoT Solutions A/S – en fælles case for 6. semester*. Erhvervsakademi København.

Delopgave 1 (2026). *Strategisk rapport af Intelligent IoT Solutions A/S* med Bilag A (Event Storming). Gruppe 9: Brian Jegindø, Mie Mosberg, Tobias Stryhn, Nicklas Vilmann og Rene Dalby. Erhvervsakademi København.

Eftekhari, J. (2026). *IOT_DEMO* [samling af eksempelkode fra undervisningen; IOT står for Internet of Things]. Tilgængelig på: https://github.com/jamshideftekhari/IOT_DEMO.

Erhvervsakademi København (2026). *Afleveringsopgave #2 – Teknisk MVP – REST API Microservice løsning*. Faget 6.2 Design og implementering af digitale løsninger.

Fielding, R.T. (2000). *Architectural Styles and the Design of Network-based Software Architectures*. Doktorafhandling. University of California, Irvine.

Ries, E. (2011). *The Lean Startup*. New York: Crown Business.

## Bilag A. Udvalgte kodeuddrag {.unnumbered .bilag}

Billederne er taget af den rigtige kode med de rigtige linjenumre. Koden er skrevet på engelsk, men alle kommentarer i koden er på dansk. Under hvert billede står der kort, **hvorfor** koden er skrevet sådan. Kodeuddrag 1 (reglerne) og kodeuddrag 4 (POST /measurements) står i selve rapporten som figur 3 og 4.

![](img/02-validering.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 2: Validering af målingen i main.py)
:::

**Hvorfor:** Pydantic tjekker data, før vores egen kode kører. En fugt på 150 eller -5 bliver afvist med fejlkode 422. Så kan reglerne stole på, at tallet er gyldigt. Det er opgavens krav om validering.

![](img/04-kvittering.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 3: Kvittering for en alarm i main.py)
:::

**Hvorfor:** Medarbejderen skal kunne sige "jeg har set den". Kvitteringen lukker ikke alarmen. Det gør kun normal fugt. Så kan man se forskel på "nogen har set problemet" og "problemet er væk". Fejlkode 404 betyder, at alarmen ikke findes, og 409, at den allerede er kvitteret.

![](img/05-tabeller.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 5: Databasens to tabeller i db.py)
:::

**Hvorfor:** Værktøjet SQLModel gør én Python-klasse til både tabellen i databasen og objektet i koden, så vi ikke skriver databasekode i hånden. Alarmens tilstand kan læses ud fra, hvilke af de tre tidspunkter der er udfyldt, så der ikke er et ekstra statusfelt, der kan komme ud af trit. Adressen på databasen kommer udefra (DATABASE_URL), så den samme kode bruger PostgreSQL i Docker og en lille testdatabase i testene.

![](img/06-pi.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 6: Programmet på Pi'en (pi/pi.py))
:::

**Hvorfor:** Pi'en måler, sender og viser svaret, men beslutter intet selv. Så kan reglerne ændres uden at røre Pi'en. Hvis serveren ikke svarer inden for 5 sekunder, hænger Pi'en ikke fast. Den lyser blåt og prøver igen. Serverens adresse sættes udefra (API_URL), så programmet virker, selvom computerens adresse skifter.

![](img/07-kontrolcenter-js.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 7: Kontrolcentrets JavaScript i static/index.html)
:::

**Hvorfor:** Én fil uden ekstra værktøjer er det mindste, der viser alarmen for medarbejderen. Siden spørger API'et hvert 3. sekund (på engelsk polling). Kun alarmer, der ikke er kvitteret, får en Kvittér-knap.

![](img/08-test-fixture.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 8: Opsætningen af testene i tests/test_mvp.py)
:::

**Hvorfor:** Hver test får sin egen tomme database i computerens hukommelse. Testene påvirker derfor ikke hinanden og kræver ikke Docker. Den rigtige database bliver byttet ud med testdatabasen, uden at koden i main.py skal ændres.

![](img/09-docker-compose.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 9: De to containere i docker-compose.yml)
:::

**Hvorfor:** Databasen kører i sin egen container, som opgaven kræver. Serveren starter først, når databasen svarer (healthcheck), ellers ville den fejle ved opstart. Data ligger i et volume, så de overlever en genstart.

![](img/10-dockerfile.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 10: Opskriften på serverens container (Dockerfile))
:::

**Hvorfor:** Pakkelisten kopieres før koden, så Docker kan genbruge de installerede pakker, når kun koden ændres. Containeren kører som en almindelig bruger og ikke som administrator (sikkerhed). Adressen 0.0.0.0 betyder, at serveren kan nås fra andre computere, for eksempel Pi'en.

![](img/11-ci.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 11: Opskriften på den automatiske kontrol (.github/workflows/ci.yml))
:::

**Hvorfor:** Kørslen starter ved hver ændring på main. Den har kun lov til at læse koden (mindst mulige rettigheder). De fire trin kører i rækkefølge, og fejler ét, stopper det hele og viser serverens log.

## Bilag B. Flere diagrammer {.unnumbered .bilag}

![](img/diagram-simpel-3-sekvens.png){width=100%}

::: {custom-style="Billedtekst"}
(Diagram 1, egen fremstilling (2026): Trin for trin, hvad der sker, når Pi'en måler 63,1 %RH, og når en medarbejder kvitterer)
:::

![](img/diagram-simpel-5-datamodel.png){width=100%}

::: {custom-style="Billedtekst"}
(Diagram 2, egen fremstilling (2026): Databasens to tabeller, measurement (Sensor Value Received) og alarm (Anomaly Detected), med kolonner og betydning)
:::

![](img/diagram-simpel-4-cicd.png){width=100%}

::: {custom-style="Billedtekst"}
(Diagram 3, egen fremstilling (2026): Den automatiske kontrol på GitHub Actions, fra ny kode til grønt flueben)
:::

## Bilag C. Hele projektets mappestruktur på GitHub {.unnumbered .bilag}

Mappestrukturen (på engelsk et treeview) viser alle filer i https://github.com/Vildmand/Delopgave2. Kun tre filer udgør selve serveren: `main.py`, `rules.py` og `db.py`.

```
Delopgave2/
├── .github/
│   └── workflows/
│       └── ci.yml                CI/CD: pip-audit → pytest → Docker → Newman
├── docs/
│   ├── img/                      kodebilleder (01–11) og diagrammer (1–6)
│   ├── KODEGUIDE.md              forklaring af koden, fil for fil
│   ├── KRAV.md                   opgavens krav → hvor de er løst
│   ├── PI-GUIDE.md               sådan startes pi.py på Pi'en
│   ├── RAPPORT.md                denne rapport
│   └── VIDEOMANUSKRIPT.md        manuskript til videoen (ca. 5 min.)
├── pi/
│   └── pi.py                     kører på Pi'en: måler, sender, farver LED
├── postman/
│   └── fugt-mvp.postman_collection.json   5 kald gennem alarmflowet
├── static/
│   └── index.html                kontrolcentret (HTML, CSS og JavaScript)
├── tests/
│   └── test_mvp.py               de 5 automatiske tests
├── .dockerignore                 filer, der ikke kommer med i containeren
├── .gitignore                    filer, git ikke skal gemme
├── Dockerfile                    opskriften på serverens container
├── README.md                     forsiden på GitHub: kom i gang og API
├── db.py                         databasen: measurement og alarm
├── docker-compose.yml            starter server og PostgreSQL
├── main.py                       REST API'et: de 4 endpoints
├── pytest.ini                    indstilling til testene
├── requirements-dev.txt          pakker kun til test
├── requirements.txt              pakker til serveren
└── rules.py                      reglerne: grøn/gul/rød, åbn og luk alarm
```

::: {custom-style="Billedtekst"}
(Bilag C, egen fremstilling (2026): Alle filer i projektets repository)
:::
