"""Fachklasse fuer Kunden (Pflichtenheft Kapitel 6.1)."""

import sqlite3

from fanshop import konfiguration


class Kunde:
    """Ein Kunde des WI Fanshops."""

    def __init__(
        self,
        name: str,
        strasse: str,
        plz: int,
        ort: str,
        newsletter_aktiv: bool = False,
        newsletter_rabatt_verfuegbar: bool = False,
        sticker_kontostand: int = 0,
        kundennummer: int | None = None,
    ) -> None:
        self.kundennummer = kundennummer        # None = noch nicht gespeichert
        self.name = name
        self.strasse = strasse
        self.plz = plz
        self.ort = ort
        self.newsletter_aktiv = newsletter_aktiv
        self.newsletter_rabatt_verfuegbar = newsletter_rabatt_verfuegbar
        self.sticker_kontostand = sticker_kontostand

    # -- berechnete Werte --------------------------------------------------

    @property
    def plz_text(self) -> str:
        """Postleitzahl immer fuenfstellig - 1067 wird wieder zu '01067'.

        Die Spalte ist laut Pflichtenheft INTEGER; fuehrende Nullen gehen dabei
        verloren. Fuer die Anzeige werden sie hier wieder ergaenzt.
        """
        return f"{self.plz:05d}"

    @property
    def anschrift(self) -> str:
        """Adresse in einer Zeile: 'Musterweg 1, 66117 Saarbrücken'."""
        return f"{self.strasse}, {self.plz_text} {self.ort}"

    @property
    def darf_newsletter_rabatt_nutzen(self) -> bool:
        """True, wenn der einmalige 10-Prozent-Gutschein noch offen ist (/F52/)."""
        return self.newsletter_aktiv and self.newsletter_rabatt_verfuegbar

    # -- Umwandlung Datenbank <-> Objekt -----------------------------------

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Kunde":
        return cls(
            kundennummer=zeile["kundennummer"],
            name=zeile["name"],
            strasse=zeile["strasse"],
            plz=zeile["plz"],
            ort=zeile["ort"],
            newsletter_aktiv=bool(zeile["newsletter_aktiv"]),
            newsletter_rabatt_verfuegbar=bool(zeile["newsletter_rabatt_verfuegbar"]),
            sticker_kontostand=zeile["sticker_kontostand"],
        )

    def als_datenbankwerte(self) -> tuple:
        return (
            self.name,
            self.strasse,
            self.plz,
            self.ort,
            1 if self.newsletter_aktiv else 0,
            1 if self.newsletter_rabatt_verfuegbar else 0,
            self.sticker_kontostand,
        )

    # -- Darstellung -------------------------------------------------------

    def __str__(self) -> str:
        if self.kundennummer is None:
            return self.name
        return f"{self.kundennummer} - {self.name}"

    def __repr__(self) -> str:
        return f"<Kunde {self.kundennummer} {self.name!r}>"


# Platzhalter fuer Bestellungen, deren Kunde geloescht wurde (/F43/).
# Die Bestellung bleibt erhalten, der Name wird anonymisiert angezeigt.
ANONYMER_KUNDENNAME = konfiguration.ANONYMER_KUNDE
