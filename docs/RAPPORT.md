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
  - ["Antal sider:", "7 (inkl. litteraturliste, uden bilag)"]
lang: da-DK
---

# Fra sensor til alarm: Fugtovervågning hos IIS {.unnumbered .del}

## 1. Problem og domæne

I delopgave 1 analyserede vi virksomheden Intelligent IoT Solutions A/S, som vi kalder IIS. IoT står for Internet of Things (på dansk "tingenes internet") og betyder, at ting som sensorer og maskiner sender data over internettet. IIS har et nyt forretningsområde, *Managed Services*, hvor de mod betaling overvåger kundernes anlæg døgnet rundt fra et kontrolcenter i Aalborg. Området forventes at stå for mindst 10 % af omsætningen inden for fem år (Casebeskrivelse, 2026). Vores analyse pegede på værdistrømmen VS7: *Få anlæg overvåget og vedligeholdt proaktivt*. En værdistrøm er de trin, en kunde går igennem for at få et resultat, og proaktivt betyder, at man handler, før noget går galt. Vi kaldte Managed Services et kerneområde, fordi det er her, IIS skiller sig ud fra konkurrenterne (Delopgave 1, 2026).

Opgaven beder os om scenariet *Predictive Maintenance / notifikation* (forudsigende vedligeholdelse og besked) med hændelserne *Sensor Value Received* (en måling er modtaget) og *Anomaly Detected* (en afvigelse er opdaget), et tjek mod en grænse som beslutning og en alarm som handling (Erhvervsakademi København, 2026). Vi har bygget det mindste, der viser hele kæden, lidt ligesom en røgalarm. En Raspberry Pi (en billig computer på størrelse med et kreditkort, herefter Pi'en) med sensorkortet Sense HAT (Hardware Attached on Top, et kort der sættes oven på Pi'en) måler luftfugtigheden og sender den til vores server. Serveren vurderer målingen og opretter en alarm, hvis fugten er for høj. En medarbejder ser alarmen på en hjemmeside og kvitterer. Alt bliver gemt i en database. For IIS' kunder er behovet færre uventede stop, fordi fugt i for eksempel et styreskab i en vindmølle kan give rust og kortslutning, længe før noget går i stykker.

Problemstillingen er: *Hvordan kan IIS med en lille webtjeneste gøre målinger fra sensorer til alarmer, som medarbejderne kan handle på i tide, og hvordan kan løsningen bygges, testes og startes automatisk?*

### 1.1. Centrale begreber og forkortelser

De vigtigste fagord står i tabel 1. Andre forkortelser bliver forklaret i en parentes, første gang de bruges.

| Begreb | Forklaring |
|-------|-----------------|
| API (Application Programming Interface) og endpoint | En fast indgang til et program, som andre programmer kan sende og hente data gennem, ligesom en skranke. Et endpoint er én adresse i API'et, fx `/measurements`. |
| REST (Representational State Transfer) | En udbredt måde at bygge et API på med internettets almindelige kommandoer GET ("hent") og POST ("send") (Fielding, 2000). |
| MVP (Minimum Viable Product) og microservice | MVP er den mindste udgave af et produkt, der virker og kan afprøves (Ries, 2011). En microservice er en lille, selvstændig webtjeneste, der løser én opgave. |
| Hændelse (på engelsk event) | En besked om noget, der allerede er sket, fx "måling modtaget" eller "alarm oprettet". |
| %RH og hysterese | %RH er relativ luftfugtighed i procent. Hysterese betyder, at alarmen starter over 60 %RH, men først slukker under 55 %RH, så den ikke blinker, når fugten vipper omkring 60. Det svarer til en termostat. |
| Docker og container | Docker pakker et program og alt, hvad det skal bruge, i en container, så det kører ens på alle computere. |
| DevSecOps og CI/CD | DevSecOps (Development, Security, Operations) er en arbejdsform, hvor udvikling, sikkerhed og drift hænger sammen. CI/CD (Continuous Integration / Continuous Delivery) er automatisk test, bygning og start af koden, hver gang den ændres. |

::: {custom-style="Billedtekst"}
(Tabel 1, egen fremstilling (2026): Begreber og forkortelser)
:::

### 1.2. Afgrænsning

Kun luftfugtighed bliver målt rigtigt. Lufttryk og rystelser vises som grå kort med teksten *Fase 2 – mockup* (en attrap med faste eksempeltal), så man kan se, hvordan løsningen kan vokse. Grænserne er valgt til demonstration og ikke til en bestemt maskine. Løsningen opdager afvigelser, når de sker, men forudsiger ikke fejl. Vi byggede først en langt større udgave, men skar den ned, så hver linje kode kan forklares og føres tilbage til opgavens krav (se afsnit 6.3).

## 2. Løsningsdesign

### 2.1. Overordnet arkitektur

Løsningen kører i Docker på en almindelig bærbar computer, og databasen kører i sin egen container ved siden af serveren, som opgaven kræver. Pi'en, testprogrammet Postman (et program til at sende testforespørgsler) og kontrolcentret taler alle med serveren gennem det samme API (se figur 1). Kun serveren bestemmer, om en måling er normal, og om der skal være en alarm. De andre viser bare, hvad serveren har besluttet.

![](img/diagram-simpel-1-arkitektur.png){width=100%}

::: {custom-style="Billedtekst"}
(Figur 1, egen fremstilling (2026): Løsningens opbygning. Pi'en sender målinger over Wi-Fi til serveren og databasen i hver sin Docker-container. Kontrolcentret i browseren henter data og kvitterer. Nederst den automatiske kontrol på GitHub)
:::

### 2.2. Event-flowet: hændelse, beslutning og handling

1. **Hændelse:** Pi'en sender en måling, fx 62,0 %RH, til `/measurements` (*Sensor Value Received*). Målingen bliver gemt.
2. **Beslutning:** Reglen siger grøn under 55 %RH, gul fra 55 til 60 og rød over 60.
3. **Handling:** Er målingen rød, og er der ikke allerede en alarm, oprettes en alarm (*Anomaly Detected*). Svaret fortæller Pi'en, at lysdisplayet skal lyse rødt.
4. **Afslutning:** En medarbejder kvitterer ("jeg har set den"). Alarmen lukker af sig selv, når fugten er under 55 %RH igen.

Figur 2 viser reglerne og en alarms liv fra oprettelse over kvittering til normal igen.

![](img/diagram-simpel-2-alarmflow.png){width=92%}

::: {custom-style="Billedtekst"}
(Figur 2, egen fremstilling (2026): Øverst farveskalaen med grænserne 55 og 60 %RH. Nederst en alarms forløb. Numrene på pilene er de tests, der kontrollerer hvert skridt)
:::

I delopgave 1 brugte vi Event Storming, en workshopmetode hvor man sætter alle hændelser i en proces op på en tidslinje (Brandolini, 2013). Den fandt kæden "Fejl rapporteret" → "Generer alert" → "ALERT genereret", som løsningen nu udfører (Delopgave 1, 2026). Tabel 2 viser, hvordan strategien er blevet til regler og tests. Hver regel har præcis én test.

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

## 3. Implementering

### 3.1. Sådan er løsningen bygget op

Løsningen er skrevet i Python med FastAPI, et værktøj til hurtigt at bygge et API, som også automatisk laver en vejledning til API'et, der hedder Swagger. Data gemmes i PostgreSQL, en gratis og udbredt database. Vi bruger Python både på Pi'en og på serveren, fordi det gør koden lettere at forklare. Hele løsningen er fem små filer (tabel 3), og al koden har forklarende kommentarer på dansk.

| Fil | Opgave | Linjer |
|---|---|---|
| `main.py` | API'et med fire endpoints: send måling, hent målinger, hent alarmer og kvittér | ca. 140 |
| `rules.py` | Reglerne som tre små funktioner, der ikke kender databasen | ca. 45 |
| `db.py` | Databasens to tabeller: `measurement` (måling) og `alarm` | ca. 65 |
| `static/index.html` | Kontrolcentret: fugten lige nu, alarmer med Kvittér-knap og mockup-kort | ca. 135 |
| `pi/pi.py` | Pi'en: læs fugten, send den og farv lysdisplayet | ca. 50 |

::: {custom-style="Billedtekst"}
(Tabel 3, egen fremstilling (2026): Kodens filer inklusive kommentarer)
:::

**Reglerne** er hjertet i løsningen (bilag A, kodeuddrag 1). De ligger i deres egen fil og kender hverken databasen, netværket eller Pi'en. **Hvorfor:** Så kan de testes på en brøkdel af et sekund, og hvis IIS vil ændre grænserne, skal det kun ske ét sted. Betingelsen `and not alarm_already_open` sørger for, at ti røde målinger i træk kun giver én alarm.

**API'et** har fire endpoints (tabel 4). Programmer bruger dem ved at sende forespørgsler over HTTP (Hypertext Transfer Protocol, det samme "sprog", en browser bruger). Endpointet, der modtager målinger, har de tre trin hændelse, beslutning og handling som tre kommentarer i koden (bilag A, kodeuddrag 4). **Hvorfor:** Det spørger reglerne i stedet for selv at sammenligne tal, så forretningsreglerne kun ligger ét sted. API'et er dokumenteret i Swagger på adressen `/docs`, hvor man også kan prøve det af, og i projektets README-fil på GitHub (projektets "læs mig først"-side).

| Hvad man gør | Adresse | Hvem bruger det |
|-------|-----|-----|
| Sende en ny måling, som serveren vurderer med det samme | POST `/measurements` | Pi'en og Postman |
| Se de seneste målinger | GET `/measurements` | Kontrolcentret |
| Se de seneste alarmer | GET `/alarms` | Kontrolcentret og Postman |
| Kvittere for en alarm | POST `/alarms/{id}/ack` | Kontrolcentret og Postman |

::: {custom-style="Billedtekst"}
(Tabel 4, egen fremstilling (2026): API'ets fire endpoints)
:::

### 3.2. Data, Pi'en og kontrolcentret

Databasen har to tabeller, som gemmer begge hændelser fra opgaven (bilag A, kodeuddrag 5). Hver række i `measurement` er en *Sensor Value Received* med enhed, fugt, farve og tidspunkt. Hver række i `alarm` er en *Anomaly Detected* med tre tidspunkter: oprettet, kvitteret og normal igen. Målingen og en eventuel alarm bliver gemt i én samlet arbejdspakke, en transaktion, så der aldrig kun bliver gemt halvdelen. Data bliver tjekket først: fugten skal ligge mellem 0 og 100 %RH, ellers svarer API'et med fejlkode 422 ("forkerte data") og gemmer intet. En alarm, der ikke findes, giver 404, og en dobbelt kvittering giver 409.

Pi'en måler hvert 5. sekund og sender til den bærbare computers adresse på netværket (`http://192.168.0.103:8000`). Det viser, at API'et kan nås fra en anden computer, som opgaven kræver. Pi'ens lysdisplay med 64 LED-lamper (Light Emitting Diode, lysdiode) lyser grønt, gult eller rødt efter serverens svar og blåt, hvis serveren ikke kan nås (kodeuddrag 6). Kontrolcentret er en hjemmeside, som serveren selv leverer. Den henter nye data hvert 3. sekund og viser fugten, alarmerne og en Kvittér-knap (bilag B, skærmbillede 1).

## 4. DevSecOps og deployment

Deployment betyder at få løsningen i gang på den computer, hvor den skal køre. Vores løsning kører lokalt i Docker og startes med én kommando: `docker compose up --build`. Den bygger koden og starter to containere: `db` med PostgreSQL og `api` med serveren, som venter, til databasen er klar. Data ligger i et Docker-volume (et lager uden for containeren), så de overlever en genstart (kodeuddrag 9 og 10).

Koden ligger på GitHub, hvor programmører gemmer og deler kode. Hver gang vi sender ny kode til hovedgrenen (main), kører GitHub Actions, GitHubs tjeneste til automatiske kørsler, de fire trin i tabel 5 af sig selv. Fejler ét trin, stopper kørslen, og fejlen kan ses på GitHub (kodeuddrag 11 og bilag B).

| Trin | Hvad sker der (værktøjets navn) |
|---|---|
| 1. Sikkerhed | Pakkerne, vi bruger, bliver tjekket for kendte sikkerhedshuller (pip-audit) |
| 2. Test | De 5 automatiske tests bliver kørt (pytest) |
| 3. Byg og start | Containeren bliver bygget, og server og PostgreSQL bliver startet på GitHubs computer |
| 4. Test af hele kæden | Postman-testene bliver kørt mod den kørende løsning (Newman, Postman til automatiske kørsler) |

::: {custom-style="Billedtekst"}
(Tabel 5, egen fremstilling (2026): Trinene i den automatiske kontrol)
:::

Den første automatiske kørsel (nummer 3, 6. november 2026) var grøn i alle trin og tog under et minut (https://github.com/Vildmand/Delopgave2/actions/runs/42223918668, bilag B, skærmbillede 2). Kørsel nummer 5 på den endelige kode med kommentarer var også grøn. CI-delen er fuldt automatisk. CD-delen kører automatisk på GitHubs computer, hvor hele løsningen startes og testes, mens den bærbare computer, som Pi'en sender til, opdateres med kommandoen ovenfor.

Sikkerheden er enkel, men med fra starten, som vi anbefalede i delopgave 1. Containeren kører ikke som administrator (root), den automatiske kontrol må kun læse koden, og pakkerne scannes ved hver ændring. Databasens adgangskode er kun til en lokal demonstration.

## 5. Kvalitet og drift

**Test.** De 5 automatiske tests svarer til de 5 regler i tabel 2 og kører på under et sekund med en tom database i hukommelsen. Postman-samlingen gennemspiller hele forløbet i 5 trin: normal måling, høj måling med alarm, hent alarmen, kvittér og en normal måling, der lukker den. Alle bestod både lokalt og på GitHub, og vi så rækkerne i PostgreSQL med psql (databasens eget spørgeprogram). Programmet er også afprøvet på den rigtige Pi over Wi-Fi: i et tørt lokale på cirka 28 %RH lyste displayet grønt, og når man puster på sensoren, bliver det rødt, og alarmen dukker op i kontrolcentret.

**Overvågning, fejlhåndtering og logning.** Kontrolcentret viser tidspunktet for den seneste måling, så man kan se, hvis Pi'en er holdt op med at sende, og Pi'en lyser blåt uden forbindelse. Forkerte data afvises med en fejlkode, og intet gemmes halvt. Fejler netværket, prøver Pi'en igen 5 sekunder senere. Serveren skriver hver forespørgsel i Docker-loggen (en slags dagbog), som man ser med `docker compose logs api`, og fejler den automatiske kontrol, viser den selv loggen. Databasen er desuden en logbog over alle målinger og alarmer.

## 6. Refleksion

### 6.1. Hvad fungerede godt

Det fungerede bedst at lade delopgave 1 styre koden. Hver regel kan føres tilbage til strategien og har én test (tabel 2). Da "Generer alert" fra Event Storming blev til "alarm oprettet" i koden, databasen og testene, blev løsningen let at forklare. Det fungerede også godt at skære ned. Vi byggede først en stor udgave med tre måletyper, en logbog over hændelser og 153 tests. Den virkede, men var svær at forklare på få minutter. Med fem filer kan man følge hele kæden, og alle opgavens krav er stadig opfyldt.

### 6.2. Hvad kunne forbedres

Vi burde have startet småt og bygget ud i stedet for omvendt. Én høj måling giver straks en alarm, så et kort pust kan give en falsk alarm. Der er intet login, så alle på netværket kan sende målinger og kvittere, og forbindelsen er ikke krypteret. Og løsningen er ikke rigtig forudsigende vedligeholdelse: en fast grænse opdager et problem nu, men forudsiger ikke et senere. Det er mere præcist at kalde den afvigelsesdetektion, som gør vedligeholdelsen proaktiv.

### 6.3. Hvordan løsningen kan videreudvikles

Den store udgave ligger urørt i vores første repository (https://github.com/miemosberg2201/RaspPI), så hvert næste skridt er allerede bygget og testet én gang. Figur 3 viser vejen område for område. Vi ville tage trinene i denne rækkefølge, med det vigtigste for forretningen først:

![](img/diagram-simpel-6-vejen-frem.png){width=100%}

::: {custom-style="Billedtekst"}
(Figur 3, egen fremstilling (2026): Vejen frem fra MVP'en nu over de næste skridt til den fulde model, som allerede er afprøvet i det første repository)
:::

1. **En mere robust regel:** alarm først efter tre høje målinger i træk og normal efter tre lave, så korte udsving ikke giver alarm. Målinger ældre end 35 sekunder markeres som forældede.
2. **En logbog over hændelser:** en tabel, hvor hændelser gemmes og aldrig kan ændres. Så kan fx en service desk (afdelingen, der opretter sager til teknikerne) læse dem. Det er første skridt mod det fælles beskedsystem (event-bus) fra delopgave 1.
3. **Flere måletyper:** lufttryk og rystelser med egne grænser, men samme regel, så mockup-kortene bliver rigtige.
4. **Kode i lag og migrationer:** koden deles i lag (forespørgsler, forløb, regler og database), og databasen ændres med migrationer (små opskrifter, der ændrer den uden at miste data).
5. **En robust Pi:** en kø (outbox), der gemmer målinger, mens netværket er nede.
6. **Sikkerhed og drift:** nøgle til hver enhed og login til hver medarbejder, krypteret forbindelse med HTTPS, flere scanninger i den automatiske kontrol (gitleaks og Trivy) og til sidst automatisk udrulning til Azure, Microsofts tjeneste til at leje computere over internettet.

Pointen med MVP'en er, at trinene kan tages ét ad gangen, når forretningen har brug for dem. Det passer med delopgave 1: teknologi skal vælges, fordi den løser et behov (Delopgave 1, 2026).

## Litteraturliste {.unnumbered}

Brandolini, A. (2013). *Introducing EventStorming*. Leanpub.

Casebeskrivelse (2026). *Intelligent IoT Solutions A/S – en fælles case for 6. semester*. Erhvervsakademi København.

Delopgave 1 (2026). *Strategisk rapport af Intelligent IoT Solutions A/S* med Bilag A (Event Storming). Gruppe 9: Brian Jegindø, Mie Mosberg, Tobias Stryhn, Nicklas Vilmann og Rene Dalby. Erhvervsakademi København.

Eftekhari, J. (2026). *IOT_DEMO* [samling af eksempelkode fra undervisningen; IOT står for Internet of Things]. Tilgængelig på: https://github.com/jamshideftekhari/IOT_DEMO.

Erhvervsakademi København (2026). *Afleveringsopgave #2 – Teknisk MVP – REST API Microservice løsning*. Faget 6.2 Design og implementering af digitale løsninger.

Fielding, R.T. (2000). *Architectural Styles and the Design of Network-based Software Architectures*. Doktorafhandling. University of California, Irvine.

Ries, E. (2011). *The Lean Startup*. New York: Crown Business.

## Bilag A. Udvalgte kodeuddrag {.unnumbered .bilag}

Billederne er taget af den rigtige kode med de rigtige linjenumre. Koden er skrevet på engelsk, men alle kommentarer i koden er på dansk. Under hvert billede står der kort, **hvorfor** koden er skrevet sådan.

![](img/01-rules.png){width=80%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 1: Reglerne i rules.py)
:::

**Hvorfor:** Reglerne er rene funktioner uden database og netværk, så de kan testes hurtigt og ændres ét sted. Grænserne 55 og 60 står øverst, så man ikke skal lede efter dem. `and not alarm_already_open` forhindrer dobbelte alarmer, og at alarmen først lukker under 55, er hysteresen.

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

![](img/03-post-measurements.png){width=92%}

::: {custom-style="Billedtekst"}
(Kodeuddrag 4: Endpointet POST /measurements i main.py, hvor en måling bliver til en farve og måske en alarm)
:::

**Hvorfor:** De tre trin hændelse, beslutning og handling står som tre kommentarer. Endpointet spørger reglerne i stedet for selv at sammenligne tal. `session.commit()` til sidst gemmer måling og alarm i én transaktion, så der aldrig opstår en alarm uden den måling, der udløste den. Svaret er det, Pi'en bruger til at farve lysdisplayet.

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

## Bilag B. Skærmbilleder og flere diagrammer {.unnumbered .bilag}

![](img/kontrolcenter.png){width=75%}

::: {custom-style="Billedtekst"}
(Skærmbillede 1: Kontrolcentret med en aktiv alarm, en alarm der er normal igen, og de grå mockup-kort til fase 2)
:::

![](img/ci-groen-koersel-3.png){width=70%}

::: {custom-style="Billedtekst"}
(Skærmbillede 2: Den grønne kørsel nummer 3 på GitHub Actions. Trinene og tiderne er gengivet fra kørslens egne data på GitHub. Kørsel 5 på den endelige kode: https://github.com/Vildmand/Delopgave2/actions/runs/42225474539)
:::

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
