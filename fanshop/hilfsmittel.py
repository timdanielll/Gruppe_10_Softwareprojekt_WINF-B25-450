"""Kleine Hilfsfunktionen, die in mehreren Schichten gebraucht werden.

Bewusst klein gehalten: hier stehen nur Funktionen ohne Fachlogik
(Formatierung, Runden, Datumsumwandlung).
"""

import time
from datetime import date, datetime


def runde_geld(betrag: float) -> float:
    """Rundet auf zwei Nachkommastellen (Cent).

    Wird nach jeder Rabattrechnung benutzt, damit keine Betraege wie
    12.340000000000002 entstehen.
    """
    return round(betrag + 0.0, 2)


def euro(betrag: float) -> str:
    """Formatiert eine Zahl als deutschen Eurobetrag: 1234.5 -> '1.234,50 €'."""
    text = f"{betrag:,.2f}"                      # 1,234.50 (englisches Format)
    text = text.replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{text} €"


def prozent(anteil: float) -> str:
    """Formatiert 0.15 als '15,0 %'."""
    return f"{anteil * 100:.1f}".replace(".", ",") + " %"


def zahl_aus_text(text: str, feldname: str = "Wert") -> float:
    """Liest eine Dezimalzahl aus einer Benutzereingabe.

    Akzeptiert deutsche und englische Schreibweise ("19,90" und "19.90"),
    weil Kassenpersonal beides tippt.

    :raises ValidierungsFehler: wenn der Text keine Zahl ist
    """
    from fanshop.fehler import ValidierungsFehler  # lokal, um Ringimporte zu vermeiden

    bereinigt = text.strip().replace("€", "").replace(" ", "").replace(",", ".")
    if not bereinigt:
        raise ValidierungsFehler(f"{feldname} darf nicht leer sein.")
    try:
        return float(bereinigt)
    except ValueError:
        raise ValidierungsFehler(
            f"„{text}“ ist keine gültige Zahl für {feldname}."
        ) from None


def ganzzahl_aus_text(text: str, feldname: str = "Wert") -> int:
    """Liest eine ganze Zahl aus einer Benutzereingabe (Mengen, Bestände, PLZ)."""
    from fanshop.fehler import ValidierungsFehler

    bereinigt = text.strip().replace(" ", "")
    if not bereinigt:
        raise ValidierungsFehler(f"{feldname} darf nicht leer sein.")
    try:
        return int(bereinigt)
    except ValueError:
        raise ValidierungsFehler(
            f"„{text}“ ist keine gültige ganze Zahl für {feldname}."
        ) from None


def heute_iso() -> str:
    """Heutiges Datum als 'YYYY-MM-DD' (ISO 8601, Pflichtenheft Kapitel 6.2)."""
    return date.today().isoformat()


def jetzt_iso() -> str:
    """Aktueller Zeitpunkt als 'YYYY-MM-DD HH:MM:SS' (fuer Retouren)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def jetzt_zeitstempel() -> int:
    """Aktueller Zeitpunkt als Unix-Zeitstempel (Pflichtenheft Kapitel 6.3)."""
    return int(time.time())


def zeitstempel_zu_text(zeitstempel: int) -> str:
    """Wandelt einen Unix-Zeitstempel in '12.06.2026 14:03' um."""
    return datetime.fromtimestamp(zeitstempel).strftime("%d.%m.%Y %H:%M")


def zeitstempel_zu_iso(zeitstempel: int) -> str:
    """Wandelt einen Unix-Zeitstempel in 'YYYY-MM-DD HH:MM:SS' um.

    Wird gebraucht, um Zeitraumgrenzen mit dem Textdatum der Retouren zu
    vergleichen. ISO-Datumstexte lassen sich direkt der Groesse nach
    vergleichen ("2026-08-01" < "2026-08-02"), deshalb kommt die Datenbank
    ohne eigene Zeitrechnung aus - und wir laufen nicht in die Zeitzonenfalle
    von SQLite, das Textdaten immer als UTC deutet.
    """
    return datetime.fromtimestamp(zeitstempel).strftime("%Y-%m-%d %H:%M:%S")


def datum_zu_zeitstempel(datum_text: str, ende_des_tages: bool = False) -> int:
    """Wandelt 'YYYY-MM-DD' in einen Unix-Zeitstempel um.

    :param ende_des_tages: True liefert 23:59:59 desselben Tages.
                           Damit ist ein Berichtszeitraum inklusive Endtag.
    """
    zeitpunkt = datetime.strptime(datum_text.strip(), "%Y-%m-%d")
    if ende_des_tages:
        zeitpunkt = zeitpunkt.replace(hour=23, minute=59, second=59)
    return int(zeitpunkt.timestamp())
