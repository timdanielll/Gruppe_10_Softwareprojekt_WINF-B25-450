"""Eigene Fehlerklassen des WI Fanshop.

Warum eigene Fehler? Die Logikschicht darf keine Dialogfenster oeffnen
(/NF21/: Logik ist unabhaengig von der GUI). Statt dessen loest sie einen
Fehler mit einem verstaendlichen deutschen Text aus. Die GUI faengt diesen
Fehler ab und zeigt den Text in einem Pop-up an (/NF11/).

Alle Fehler erben von ``FanshopFehler``. Die GUI muss deshalb nur
``except FanshopFehler`` schreiben und faengt damit alle fachlichen Probleme.
"""


class FanshopFehler(Exception):
    """Basisklasse fuer alle fachlichen Fehler des Programms."""


class ValidierungsFehler(FanshopFehler):
    """Eine Eingabe ist unvollstaendig oder unplausibel.

    Beispiel: Preis ist keine Zahl, Titel ist leer, Menge ist 0.
    """


class BestandsFehler(FanshopFehler):
    """Der gewuenschte Lagerbestand reicht nicht aus (/F11/)."""


class NichtGefundenFehler(FanshopFehler):
    """Ein angefragter Datensatz existiert nicht (z. B. unbekannte Bestellnummer)."""
