"""Berichtswesen fuer die Geschaeftsfuehrung (/F31/, /F311/ bis /F313/).

Die GUI liefert zwei Datumsangaben als Text ("2026-08-01"), dieser Service
rechnet sie in Unix-Zeitstempel um und stellt die Kennzahlen zusammen.
"""

from fanshop.fehler import ValidierungsFehler
from fanshop.hilfsmittel import (
    datum_zu_zeitstempel,
    heute_iso,
    jetzt_zeitstempel,
)
from fanshop.repositories.bericht_repository import BerichtRepository

# Schnellwahl aus dem Pflichtenheft, Kapitel 7.5
ZEITRAUM_GESAMT = "gesamt"
ZEITRAUM_TAG = "tag"
ZEITRAUM_WOCHE = "woche"
ZEITRAUM_MONAT = "monat"

SEKUNDEN_PRO_TAG = 24 * 60 * 60


class Bericht:
    """Ein fertiger Bericht - alle Zahlen fuer einen Zeitraum an einem Ort."""

    def __init__(
        self,
        von_zeitstempel: int,
        bis_zeitstempel: int,
        kennzahlen: dict,
        umsatzanteile: list[dict],
        umsatz_je_kategorie: list[dict],
    ) -> None:
        """Sammelt die Kennzahlen eines Zeitraums."""
        self.von_zeitstempel = von_zeitstempel
        self.bis_zeitstempel = bis_zeitstempel
        self.kennzahlen = kennzahlen                # /F311/, /F312/
        self.umsatzanteile = umsatzanteile          # /F313/
        self.umsatz_je_kategorie = umsatz_je_kategorie  # Datenbasis Diagramm

    @property
    def anzahl_bestellungen(self) -> int:
        """Wie viele Bestellungen fielen in den Zeitraum?"""
        return self.kennzahlen["anzahl_bestellungen"]

    @property
    def umsatz(self) -> float:
        """Bruttoumsatz des Zeitraums."""
        return self.kennzahlen["umsatz"]

    @property
    def ist_leer(self) -> bool:
        """True, wenn es im Zeitraum keine Bestellung gab."""
        return self.anzahl_bestellungen == 0


class BerichtService:
    """Erzeugt die Auswertungen fuer die Shop-Leitung."""

    def __init__(self, bericht_repository: BerichtRepository) -> None:
        """Merkt sich das Bericht-Repository."""
        self.bericht_repository = bericht_repository

    # -- Zeitraum bestimmen ------------------------------------------------

    def zeitraum_schnellwahl(self, auswahl: str) -> tuple[int, int]:
        """Uebersetzt die Schnellwahl-Buttons in einen Zeitraum (/F31/).

        :param auswahl: ``"gesamt"``, ``"tag"``, ``"woche"`` oder ``"monat"``
        :return: (von_zeitstempel, bis_zeitstempel)
        """
        jetzt = jetzt_zeitstempel()

        if auswahl == ZEITRAUM_GESAMT:
            start = self.bericht_repository.erste_bestellung_zeitstempel()
            return start, jetzt
        if auswahl == ZEITRAUM_TAG:
            return datum_zu_zeitstempel(heute_iso()), jetzt
        if auswahl == ZEITRAUM_WOCHE:
            return jetzt - 7 * SEKUNDEN_PRO_TAG, jetzt
        if auswahl == ZEITRAUM_MONAT:
            return jetzt - 30 * SEKUNDEN_PRO_TAG, jetzt

        raise ValidierungsFehler(f"Unbekannter Zeitraum: {auswahl}")

    def zeitraum_aus_datum(self, von_datum: str, bis_datum: str) -> tuple[int, int]:
        """Uebersetzt zwei Kalendereingaben ('YYYY-MM-DD') in einen Zeitraum.

        Der Endtag zaehlt vollstaendig mit (bis 23:59:59) - sonst wuerde ein
        Bericht "vom 1. bis 1. August" nichts anzeigen.
        """
        try:
            von = datum_zu_zeitstempel(von_datum)
            bis = datum_zu_zeitstempel(bis_datum, ende_des_tages=True)
        except ValueError:
            raise ValidierungsFehler(
                "Bitte das Datum im Format JJJJ-MM-TT eingeben, z. B. 2026-08-01."
            ) from None

        if von > bis:
            raise ValidierungsFehler("Das Startdatum liegt nach dem Enddatum.")
        return von, bis

    # -- /F31/ Bericht erzeugen --------------------------------------------

    def bericht_erstellen(self, von_zeitstempel: int, bis_zeitstempel: int) -> Bericht:
        """Stellt alle Kennzahlen eines Zeitraums zusammen (/F31/)."""
        return Bericht(
            von_zeitstempel=von_zeitstempel,
            bis_zeitstempel=bis_zeitstempel,
            kennzahlen=self.bericht_repository.kennzahlen(von_zeitstempel, bis_zeitstempel),
            umsatzanteile=self.bericht_repository.umsatzanteile(von_zeitstempel, bis_zeitstempel),
            umsatz_je_kategorie=self.bericht_repository.umsatz_je_kategorie(
                von_zeitstempel, bis_zeitstempel
            ),
        )
