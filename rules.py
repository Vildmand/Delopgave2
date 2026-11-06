"""rules.py - domænereglerne (beslutningen i flowet "event -> beslutning -> handling").

Reglerne er rene funktioner: de får en fugtværdi og svarer. De kender hverken
database, HTTP eller Raspberry Pi. Derfor er de nemme at teste og forklare,
og de kan ændres ét sted uden at røre resten af koden.

Grænser (demoværdier, ikke industrielle grænser):
    under 55 %RH      -> grøn  (normal)
    55 til 60 %RH     -> gul   (advarsel, ingen alarm endnu)
    over 60 %RH       -> rød   (afvigelse: der åbnes en alarm)

Normalisering: en åben alarm lukkes først, når fugten er under 55 igen.
Afstanden mellem 60 og 55 (hysterese) gør, at alarmen ikke blinker
op og ned, hvis fugten ligger og vipper omkring 60. Det virker som en termostat.
"""

# Grænserne står som konstanter øverst, så de kan ændres ét sted.
ALARM_OVER = 60.0  # over denne værdi: rød + alarm (Anomaly Detected)
NORMAL_UNDER = 55.0  # under denne værdi: grøn + åben alarm lukkes


def status(humidity: float) -> str:
    """Oversæt en fugtmåling til en farve: 'green', 'yellow' eller 'red'.

    Eksempler: 48 -> green, 55 -> yellow, 60 -> yellow, 60.1 -> red.
    """
    if humidity > ALARM_OVER:  # strengt over 60: rød
        return "red"
    if humidity >= NORMAL_UNDER:  # 55 til og med 60: gul
        return "yellow"
    return "green"  # alt under 55: grøn


def should_open_alarm(humidity: float, alarm_already_open: bool) -> bool:
    """Ny alarm kun hvis målingen er rød OG der ikke allerede er en åben alarm.

    Den anden betingelse forhindrer dubletter: 10 røde målinger i træk giver én alarm.
    """
    return status(humidity) == "red" and not alarm_already_open


def should_close_alarm(humidity: float) -> bool:
    """En åben alarm normaliseres (lukkes), når fugten er tilbage under 55.

    Bemærk: 57 (gul) lukker ikke alarmen. Fugten skal helt ned i grøn.
    """
    return humidity < NORMAL_UNDER
