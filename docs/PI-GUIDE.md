# Guide: kør pi.py på Raspberry Pi'en

Forudsætning: Docker-stakken kører på PC'en (`docker compose up -d` i projektmappen), og Pi'en og PC'en er på samme netværk.

## 1. Find PC'ens IP-adresse (PowerShell på PC'en)

```powershell
ipconfig
```

Brug **IPv4 Address** under Wi-Fi, fx `192.168.0.104`.
Tjek fra PC'en, at API'et svarer: `curl.exe http://<IP>:8000/alarms` skal give `[]` eller en liste.

## 2. Kopiér pi.py til Pi'en (PowerShell, i projektmappen)

```powershell
scp pi\pi.py nicklas@NicklasRPI.local:~/
```

## 3. Log ind på Pi'en og start programmet

```powershell
ssh nicklas@NicklasRPI.local
```

Stop først den gamle klient, hvis den kører (Ctrl+C i dens vindue, eller `pkill -f sensor_client`).
Start så den nye:

```bash
API_URL=http://<IP>:8000 python3 pi.py
```

Der skrives en linje hvert 5. sekund, fx `47.9 %RH -> green`.

## 4. Demo

1. LED-displayet lyser grønt. Kontrolcentret (http://localhost:8000) viser fugten.
2. Pust på Sense HAT'en. Over 60 %RH bliver LED'en rød, og alarmen dukker op i kontrolcentret.
3. Tryk **Kvittér**. Alarmen står nu som *kvitteret*.
4. Vent, til fugten er under 55 %RH. LED'en bliver grøn, og alarmen står som *normaliseret*.

Stop med Ctrl+C.

## Fejlfinding

| Symptom | Årsag og løsning |
|---|---|
| LED'en er blå, og der står "ingen forbindelse" | Forkert IP, eller Windows Firewall blokerer port 8000. Tjek IP'en med `ipconfig`, og test fra Pi'en: `curl http://<IP>:8000/alarms` |
| `ModuleNotFoundError: sense_hat` | `sudo apt install sense-hat` |
| `ModuleNotFoundError: requests` | `sudo apt install python3-requests` |
| `ssh: Could not resolve hostname` | Brug Pi'ens IP i stedet, fx `nicklas@192.168.0.106` |
