"""pi.py - kører på Raspberry Pi'en med Sense HAT. Start: python3 pi.py

Hvert 5. sekund:
    1. Læs luftfugtigheden fra Sense HAT'en.
    2. Send den til REST API'et med en HTTP POST (det er eventet "Sensor Value Received").
    3. Farv hele LED-displayet efter API'ets svar: grøn, gul eller rød.
       Blå betyder, at Pi'en ikke kan få fat i serveren.

Pi'en tager ingen beslutninger selv. Reglerne ligger kun på serveren (rules.py),
så de kan ændres ét sted.

Serverens adresse sættes med miljøvariablen API_URL, fx:
    API_URL=http://192.168.0.103:8000 python3 pi.py
"""

import os  # læser miljøvariablerne API_URL og DEVICE_ID
import time  # time.sleep() venter mellem målingerne

import requests  # sender HTTP-forespørgsler til API'et
from sense_hat import SenseHat  # findes kun på Pi'en (sudo apt install sense-hat)

# Indstillinger. os.getenv(navn, standard) bruger standardværdien, hvis variablen mangler.
API_URL = os.getenv("API_URL", "http://192.168.0.103:8000")  # serverens adresse
DEVICE_ID = os.getenv("DEVICE_ID", "pi-01")  # Pi'ens navn i databasen
INTERVAL_SECONDS = 5  # hvor ofte der måles

# LED-farver som (rød, grøn, blå), hver fra 0 til 255. Nøglerne er API'ets svar.
COLORS = {"green": (0, 150, 0), "yellow": (200, 140, 0), "red": (200, 0, 0)}
NO_CONNECTION = (0, 0, 150)  # blå: serveren svarer ikke

sense = SenseHat()  # forbindelsen til Sense HAT'ens sensorer og LED-display

while True:  # kør for evigt (stop med Ctrl+C)
    # 1. Læs fugten, og afrund til én decimal (fx 48.237... -> 48.2).
    #    Sensoren kan vise lidt over 100, når man puster direkte på den. API'et
    #    godtager kun 0-100 %RH, så min(..., 100.0) holder værdien inden for det gyldige.
    humidity = min(round(sense.get_humidity(), 1), 100.0)
    try:
        # 2. Send målingen som JSON. timeout=5: giv op efter 5 sekunder uden svar.
        response = requests.post(
            f"{API_URL}/measurements",
            json={"device_id": DEVICE_ID, "humidity": humidity},
            timeout=5,
        )
        response.raise_for_status()  # fejl hvis serveren svarer 4xx/5xx
        status = response.json()["status"]  # serverens beslutning: green/yellow/red
        # 3. Farv hele displayet i den farve, serveren bestemte.
        sense.clear(COLORS[status])
        print(f"{humidity} %RH -> {status}")
    except requests.RequestException as error:
        # Ingen forbindelse, timeout eller fejlsvar: vis blå, og prøv igen næste gang.
        sense.clear(NO_CONNECTION)
        print(f"{humidity} %RH -> ingen forbindelse: {error}")
    time.sleep(INTERVAL_SECONDS)  # vent 5 sekunder før næste måling
