"""Fachklasse fuer Retouren (Pflichtenheft Kapitel 6.5, Anforderung /F51/).

Eine Retoure haengt an einer **Bestellposition**, nicht nur an einem Artikel:
Seit die Groesse beim Bestellen gewaehlt wird, kann derselbe Artikel in einer
Bestellung zweimal vorkommen (etwa ein Hoodie in M und einer in L). Nur die
Positionsnummer sagt eindeutig, welche der beiden Zeilen zurueckgeht.
"""

import sqlite3

from fanshop.hilfsmittel import jetzt_iso


class Retoure:
    """Die Rueckgabe einer Position aus einer frueheren Bestellung."""

    def __init__(
        self,
        bestellnummer: int,
        artikel_id: int,
        menge: int,
        erstattungsbetrag: float,
        position_id: int | None = None,
        retouren_datum: str | None = None,
        artikel_titel: str = "",
        groesse: str = "",
        retouren_id: int | None = None,
    ) -> None:
        """Legt einen Retourenbeleg an."""
        self.retouren_id = retouren_id
        self.bestellnummer = bestellnummer
        #: Auf welche Bestellzeile sich die Rueckgabe bezieht (/F51/).
        self.position_id = position_id
        self.artikel_id = artikel_id
        self.menge = menge
        self.erstattungsbetrag = erstattungsbetrag
        self.retouren_datum = retouren_datum or jetzt_iso()
        self.artikel_titel = artikel_titel      # nur fuer die Anzeige
        self.groesse = groesse                  # nur fuer die Anzeige

    @property
    def anzeigename(self) -> str:
        """Titel, bei Kleidung mit angehaengter Groesse."""
        if self.groesse:
            return f"{self.artikel_titel} (Gr. {self.groesse})"
        return self.artikel_titel

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Retoure":
        """Baut eine Retoure aus einer Datenbankzeile."""
        schluessel = zeile.keys()
        return cls(
            retouren_id=zeile["retouren_id"],
            bestellnummer=zeile["bestellnummer"],
            position_id=zeile["position_id"] if "position_id" in schluessel else None,
            artikel_id=zeile["artikel_id"],
            menge=zeile["menge"],
            erstattungsbetrag=zeile["erstattungsbetrag"],
            retouren_datum=zeile["retouren_datum"],
            artikel_titel=zeile["artikel_titel"] if "artikel_titel" in schluessel else "",
            groesse=(zeile["groesse"] or "") if "groesse" in schluessel else "",
        )

    def __str__(self) -> str:
        """Kurzfassung fuer Listen und Fehlersuche."""
        return (
            f"Retoure {self.retouren_id}: {self.menge} x "
            f"{self.anzeigename or self.artikel_id} aus Bestellung {self.bestellnummer}"
        )
