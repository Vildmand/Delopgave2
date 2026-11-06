"""pi.py - kører på Raspberry Pi'en med Sense HAT. Start: python3 pi.py

Hvert 5. sekund:
    1. Læs luftfugtigheden fra Sense HAT'en.
    2. Send den til REST API'et med en HTTP POST (det er eventet "Sensor Value Received").
    3. Farv hele LED-displayet efter API'ets svar: grøn, gul eller rød.
       Blå betyder, at Pi'en ikke kan få fat i serveren.

Pi'en tager ingen beslutninger selv. Reglerne ligger kun på serveren (rules.py),
så de kan ændres ét sted.

Serverens adresse sættes med miljøvariablen API_URL, fx:
    API_URL=http://192.168.0.104:8000 python3 pi.py
"""

import os
import time

import requests
from sense_hat import SenseHat  # findes kun på Pi'en (sudo apt install sense-hat)

API_URL = os.getenv("API_URL", "http://192.168.0.104:8000")
DEVICE_ID = os.getenv("DEVICE_ID", "pi-01")
INTERVAL_SECONDS = 5

COLORS = {"green": (0, 150, 0), "yellow": (200, 140, 0), "red": (200, 0, 0)}
NO_CONNECTION = (0, 0, 150)  # blå

sense = SenseHat()

while True:
    humidity = round(sense.get_humidity(), 1)
    try:
        response = requests.post(
            f"{API_URL}/measurements",
            json={"device_id": DEVICE_ID, "humidity": humidity},
            timeout=5,
        )
        response.raise_for_status()  # fejl hvis serveren svarer 4xx/5xx
        status = response.json()["status"]
        sense.clear(COLORS[status])  # hele displayet i én farve
        print(f"{humidity} %RH -> {status}")
    except requests.RequestException as error:
        sense.clear(NO_CONNECTION)
        print(f"{humidity} %RH -> ingen forbindelse: {error}")
    time.sleep(INTERVAL_SECONDS)
