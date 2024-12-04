# Systemintegration_Labb2
Författare: Pontus Brusewitz & Walid Soboh

**Översikt av Systemet:**
Systemet består av flera delar som samarbetar för att samla in, vidarebefordra, bearbeta och presentera data:

**Embedded-Enhet (Simulerad):**
Denna del av systemet simulerar en embedded-enhet som samlar in sensordata (till exempel antal lyssnare).
Data skickas från den simulerade enheten till en MQTT-broker.

**MQTT-Broker (Mosquitto):**
Vi använder oss av MQTT-brokern Mosquitto. Den hanterar meddelanden som skickas från den simulerade enheten.
Brokern tar emot och lagrar sensordata som sedan kan hämtas av prenumeranter.

**Flask API-Server:**
Flask-applikationen agerar som en API-server. Den prenumererar på MQTT-brokern för att hämta sensordata.
Flask-applikationen tillhandahåller även ett webbgränssnitt för användare att se data, både från MQTT och från externa API:er (som Sveriges Radio API).

**API-Gateway (APISIX):**
APISIX fungerar som en mellanhand mellan användarna (klienterna) och Flask API-servern.
Den hanterar och dirigerar inkommande förfrågningar till rätt destination (Flask-servern), och kan tillhandahålla ytterligare funktioner som säkerhetskontroller, rate limiting och caching.

**Klient (Webbläsare):**
Användare interagerar med systemet via en webbläsare. De gör förfrågningar som går igenom APISIX och når Flask-servern, som sedan returnerar begärd data.

**Hur Komponenterna Samverkar:**

**Dataflöde:**
Data flödar från den simulerade enheten till MQTT-brokern och vidare till Flask-applikationen. Flask-applikationen kan också hämta data från externa källor som Sveriges Radio API.

**Användarinteraktion:**
När en användare vill se data, görs en webbförfrågan som först når APISIX. APISIX analyserar förfrågan och vidarebefordrar den till Flask-applikationen. Flask bearbetar förfrågan och returnerar lämplig data (antingen från MQTT-brokern eller externa API:er) tillbaka till användaren via APISIX.

**Säkerhet och Effektivitet:**
Genom att använda APISIX som en API-gateway kan vi lägga till ytterligare säkerhets- och effektivitetsfunktioner i systemet, som att hantera stora mängder förfrågningar och skydda ditt API från oönskad trafik.

**Sammanfattning**
Systemet är designat för att vara en integrerad lösning som samlar in data från en simulerad sensor, vidarebefordrar denna data genom en MQTT-broker, bearbetar och tillgängliggör data via en Flask-baserad API-server, och slutligen tillhandahåller data till användare via en API-gateway. Detta tillåter en säker, effektiv och skalbar arkitektur för att hantera sensordata och integration med externa API:er.






# Systemintegrationsprojekt

## Projektöversikt

Detta projekt demonstrerar integrationen av flera teknologier för att skapa ett komplext API-system. Det innefattar en simulerad embedded-enhet, en MQTT-broker, en Flask-baserad API-server, en API-gateway (APISIX), och slutanvändarinteraktion via en webbläsare.

### Komponenter

1. **Simulerad Embedded-Enhet**:
   - Skickar sensordata (t.ex. temperaturvärden) via MQTT-protokollet.

2. **MQTT-Broker (Mosquitto)**:
   - Mottar och hanterar sensordata från den simulerade enheten.

3. **Flask API-Server**:
   - Prenumererar på MQTT-brokern för att få sensordata.
   - Tillhandahåller ett REST API för att visa sensordata och data hämtat från Sveriges Radio API.

4. **API-Gateway (APISIX)**:
   - Hanterar och dirigerar trafik från klienter till Flask API-servern.
   - Tillämpar säkerhets- och effektivitetsfunktioner som rate limiting och caching.

5. **Klient (Webbläsare)**:
   - Användare interagerar med systemet genom att göra förfrågningar via en webbläsare.

### Samverkan mellan Komponenterna

- Data skickas från den simulerade enheten till MQTT-brokern och vidare till Flask-servern, som bearbetar och tillgängliggör datan.
- Användare gör förfrågningar via en webbläsare som passerar genom APISIX, som sedan dirigerar förfrågningarna till Flask-servern.
- Flask-servern svarar med begärd data, som passerar tillbaka genom APISIX till användarens webbläsare.

## Installation och Körning

För att köra detta projekt, följ stegen nedan:

### Förberedelser

1. **Klona Repo**:
   
   Från hemsidan: https://github.com/apache/apisix-docker
   Skriv detta i terminalen dit du vill klona repot:
      ```sh
      git clone https://github.com/apache/apisix-docker.git
      ```
   Vi körde även detta kommando för att få tillgång till dasboarden:(se till att den finns med)
      ```sh
      git checkout release/apisix-dashboard-3.0.1
      ```

2. **Installera nödvändiga program/paket**:
   - Se till att du har Docker och Docker Compose installerat på din dator.
   - Installera nödvändiga Python-paket för Flask och MQTT:
     ```sh
     pip install Flask paho-mqtt requests
     ```

### Starta Komponenterna

1. **Starta MQTT-Broker (Mosquitto)**:
   ```sh
   mosquitto
   ```

2. **Kör Flask-applikationen**:
   ```sh
   python app.py
   ```

3. **Kör Simuleringskriptet för den Embedded Enheten**:
   ```sh
   python Simuleringskript.py
   ```

4. **Starta APISIX med Docker Compose**:

APISIX är en viktig del av vår projektarkitektur, och vi använder den för att hantera och dirigerar trafik samt tillhandahålla säkerhets- och effektivitetsfunktioner som autentisering, rate limiting och caching.

   - Se till att ha igång Docker
   - Gå till mappen där du sparade git-klonen från tidigare. Leta upp example mappen och gå in i terminalen därifrån.
     Kör följande kommando:
   ```bash
   docker-compose -p docker-apisix up -d
   ```
### Konfiguration APISIX
APISIX kan konfigureras via sin Dashboard, som tillåter dig att ställa in routes, services, och plugins.

Access APISIX Dashboard:

Navigera till http://localhost:9080 i din webbläsare.
Konfigurera Routes och Services:

Skapa nya routes och associera dem med de tjänster du vill exponera.
Konfigurera plugins såsom Basic Auth, rate limiting och caching för att öka säkerheten och effektiviteten i ditt system.




### APISIX Konfigurationer

Efter installationen av APISIX, använd följande konfigurationer för att sätta upp ditt system:

#### Routes och Upstreams

- **Route till Flask API-Server**:
  - **Path**: `/*
  - **Upstream URL**: `host.docker.internal:5000`
  - **Beskrivning**: Denna route dirigerar förfrågningar till Flask API-servern.

#### Plugins

1. **Basic Authentication (basic-auth)**:
   - **Konfiguration**: Ställ in användarnamn och lösenord för att skydda dina API-rutter. Exempel:
     - Användarnamn: `admin`
     - Lösenord: `admin123`

2. **Rate Limiting (limit-count och limit-req)**:
   - **limit-count**:
     - **count**: 10
     - **time_window**: 60 (sekunder)
     - **Beskrivning**: Begränsar användare till 10 förfrågningar per minut.
   - **limit-req**:
     - **rate**: 2
     - **burst**: 5
     - **Beskrivning**: Begränsar antalet förfrågningar till 2 per sekund med möjlighet till en burst av 5 förfrågningar.

3. **Proxy Cache (proxy-cache)**:
   - **cache_ttl**: 30 (sekunder)
   - **Beskrivning**: Cachar svar i 30 sekunder för att förbättra prestandan.

#### Consumer Konfiguration

- **Consumer Name**: `example_consumer`
- **Plugins Konfiguration för Consumer**:
  - **Basic Auth Credentials**:
    - Användarnamn: `example_user`
    - Lösenord: `example_password`

### Testning och Validering

- För att testa **Basic Authentication**, använd `curl` med basicauth-header:
  ```bash
  curl -u example_user:example_password http://localhost:9080/api/your_endpoint
  ```
- Testa **Rate Limiting** genom att göra upprepade förfrågningar till din route och observera när 429 Too Many Requests-felmeddelanden börjar visas.
- För att verifiera **Proxy Cache**, gör en förfrågan till din API och kontrollera `Age`-headern i svaret för att se om det cachas.

Observera att dessa värden är bara exempel och bör anpassas efter ditt systems krav och trafikmönster. Genom att använda dessa konfigurationer kan du säkerställa att ditt system är väl skyddat och hanterar trafik effektivt.

### Använda Applikationen

1. **Tillgång via Webbläsare**:
   - Öppna en webbläsare och navigera till `http://localhost:9080/` för att interagera med Flask-applikationen via APISIX.

2. **Felsökning**:
   - Använd loggarna från Mosquitto, Flask och APISIX för att felsöka eventuella problem.
