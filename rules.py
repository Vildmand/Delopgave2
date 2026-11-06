"""rules.py - domænereglerne (beslutningen i flowet "event -> beslutning -> handling").

Reglerne er rene funktioner: de får en fugtværdi og svarer. De kender hverken
database, HTTP eller Raspberry Pi. Derfor er de nemme at teste og forklare.

Grænser (demoværdier, ikke industrielle grænser):
    under 55 %RH      -> grøn  (normal)
    55 til 60 %RH     -> gul   (advarsel, ingen alarm endnu)
    over 60 %RH       -> rød   (afvigelse: der åbnes en alarm)

Normalisering: en åben alarm lukkes først, når fugten er under 55 igen.
Afstanden mellem 60 og 55 (hysterese) gør, at alarmen ikke blinker
op og ned, hvis fugten ligger og vipper omkring 60.
"""

ALARM_OVER = 60.0  # over denne værdi: rød + alarm (Anomaly Detected)
NORMAL_UNDER = 55.0  # under denne værdi: grøn + åben alarm lukkes


def status(humidity: float) -> str:
    """Oversæt en fugtmåling til en farve: 'green', 'yellow' eller 'red'."""
    if humidity > ALARM_OVER:
        return "red"
    if humidity >= NORMAL_UNDER:
        return "yellow"
    return "green"


def should_open_alarm(humidity: float, alarm_already_open: bool) -> bool:
    """Ny alarm kun hvis målingen er rød OG der ikke allerede er en åben alarm.

    Den anden betingelse forhindrer dubletter: 10 røde målinger i træk giver én alarm.
    """
    return status(humidity) == "red" and not alarm_already_open


def should_close_alarm(humidity: float) -> bool:
    """En åben alarm normaliseres (lukkes), når fugten er tilbage under 55."""
    return humidity < NORMAL_UNDER
