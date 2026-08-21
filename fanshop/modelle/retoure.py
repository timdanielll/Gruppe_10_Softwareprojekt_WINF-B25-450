"""Fachklasse fuer Retouren (Pflichtenheft Kapitel 6.5, Anforderung /F51/)."""

import sqlite3

from fanshop.hilfsmittel import jetzt_iso


class Retoure:
    """Die Rueckgabe eines Artikels aus einer frueheren Bestellung."""

    def __init__(
        self,
        bestellnummer: int,
        artikel_id: int,
        menge: int,
        erstattungsbetrag: float,
        retouren_datum: str | None = None,
        artikel_titel: str = "",
        retouren_id: int | None = None,
    ) -> None:
        self.retouren_id = retouren_id
        self.bestellnummer = bestellnummer
        self.artikel_id = artikel_id
        self.menge = menge
        self.erstattungsbetrag = erstattungsbetrag
        self.retouren_datum = retouren_datum or jetzt_iso()
        self.artikel_titel = artikel_titel      # nur fuer die Anzeige

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Retoure":
        schluessel = zeile.keys()
        return cls(
            retouren_id=zeile["retouren_id"],
            bestellnummer=zeile["bestellnummer"],
            artikel_id=zeile["artikel_id"],
            menge=zeile["menge"],
            erstattungsbetrag=zeile["erstattungsbetrag"],
            retouren_datum=zeile["retouren_datum"],
            artikel_titel=zeile["artikel_titel"] if "artikel_titel" in schluessel else "",
        )

    def __str__(self) -> str:
        return (
            f"Retoure {self.retouren_id}: {self.menge} x "
            f"{self.artikel_titel or self.artikel_id} aus Bestellung {self.bestellnummer}"
        )
