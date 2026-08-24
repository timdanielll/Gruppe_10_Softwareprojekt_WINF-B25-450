"""Fachklassen fuer Bestellungen und Bestellpositionen (Kapitel 6.3 und 6.4).

Eine Bestellung ist der gespeicherte Beleg eines abgeschlossenen Einkaufs.
Sie besteht aus mehreren Bestellpositionen (je Artikel eine Zeile).
"""

import sqlite3

from fanshop import konfiguration
from fanshop.hilfsmittel import jetzt_zeitstempel, zeitstempel_zu_text


class Bestellposition:
    """Eine Zeile einer Bestellung: welcher Artikel, wie oft, zu welchem Preis."""

    def __init__(
        self,
        artikel_id: int,
        menge: int,
        historischer_preis: float,
        artikel_titel: str = "",
        groesse: str = "",
        bestellnummer: int | None = None,
        position_id: int | None = None,
    ) -> None:
        """Legt eine Bestellzeile an."""
        self.position_id = position_id
        self.bestellnummer = bestellnummer
        self.artikel_id = artikel_id
        self.menge = menge
        # Der Preis wird mitgespeichert, weil sich der Artikelpreis spaeter
        # aendern kann. Fuer Retouren zaehlt der Preis vom Kauftag (/F51/).
        self.historischer_preis = historischer_preis
        # Die beim Kauf gewaehlte Groesse; leer bei allem ohne Groesse (/F11/).
        self.groesse = groesse
        # Nur fuer die Anzeige - kommt aus einem JOIN mit der Artikeltabelle.
        self.artikel_titel = artikel_titel

    @property
    def zeilensumme(self) -> float:
        """Menge mal gezahltem Einzelpreis."""
        return round(self.menge * self.historischer_preis, 2)

    @property
    def anzeigename(self) -> str:
        """Titel, bei Kleidung mit angehaengter Groesse."""
        if self.groesse:
            return f"{self.artikel_titel} (Gr. {self.groesse})"
        return self.artikel_titel

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Bestellposition":
        """Baut eine Bestellzeile aus einer Datenbankzeile."""
        schluessel = zeile.keys()
        return cls(
            position_id=zeile["position_id"],
            bestellnummer=zeile["bestellnummer"],
            artikel_id=zeile["artikel_id"],
            menge=zeile["menge"],
            historischer_preis=zeile["historischer_preis"],
            groesse=(zeile["groesse"] or "") if "groesse" in schluessel else "",
            artikel_titel=zeile["artikel_titel"] if "artikel_titel" in schluessel else "",
        )

    def __str__(self) -> str:
        """Menge mal Anzeigename."""
        return f"{self.menge} x {self.anzeigename or self.artikel_id}"


class Bestellung:
    """Ein abgeschlossener Einkauf inklusive Rechnung (/F14/)."""

    def __init__(
        self,
        kundennummer: int | None,
        gesamtbetrag: float,
        zeitstempel: int | None = None,
        newsletter_rabatt_angewendet: bool = False,
        sticker_ausgegeben: int = konfiguration.STICKER_PRO_EINKAUF,
        starterset_ausgegeben: bool = False,
        kundenname: str | None = None,
        bestellnummer: int | None = None,
        positionen: list[Bestellposition] | None = None,
    ) -> None:
        """Legt einen Bestellbeleg mit allen Kopfdaten an."""
        self.bestellnummer = bestellnummer
        self.kundennummer = kundennummer        # None = Kunde wurde geloescht
        self.zeitstempel = zeitstempel or jetzt_zeitstempel()
        self.gesamtbetrag = gesamtbetrag
        self.newsletter_rabatt_angewendet = newsletter_rabatt_angewendet
        self.sticker_ausgegeben = sticker_ausgegeben
        # True, wenn dieser Bestellung das Starterset beilag (/F53/).
        self.starterset_ausgegeben = starterset_ausgegeben
        self.kundenname = kundenname            # nur fuer die Anzeige
        self.positionen = positionen or []

    @property
    def datum_text(self) -> str:
        """Zeitstempel lesbar als '12.06.2026 14:03'."""
        return zeitstempel_zu_text(self.zeitstempel)

    @property
    def kunde_anzeige(self) -> str:
        """Kundenname oder Hinweis auf anonymisierte Bestellung (/F43/)."""
        if self.kundennummer is None:
            return konfiguration.ANONYMER_KUNDE
        return self.kundenname or f"Kunde {self.kundennummer}"

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Bestellung":
        """Baut eine Bestellung aus einer Datenbankzeile (ohne Positionen)."""
        schluessel = zeile.keys()
        return cls(
            bestellnummer=zeile["bestellnummer"],
            kundennummer=zeile["kundennummer"],
            zeitstempel=zeile["zeitstempel"],
            gesamtbetrag=zeile["gesamtbetrag"],
            newsletter_rabatt_angewendet=bool(zeile["newsletter_rabatt_angewendet"]),
            sticker_ausgegeben=zeile["sticker_ausgegeben"],
            starterset_ausgegeben=bool(zeile["starterset_ausgegeben"])
            if "starterset_ausgegeben" in schluessel
            else False,
            kundenname=zeile["kundenname"] if "kundenname" in schluessel else None,
        )

    def __str__(self) -> str:
        """Bestellnummer und Datum."""
        return f"Bestellung {self.bestellnummer} vom {self.datum_text}"
