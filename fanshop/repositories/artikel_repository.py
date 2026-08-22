"""Datenzugriff fuer Artikel (/F21/ bis /F25/)."""

from fanshop.modelle.artikel import Artikel
from fanshop.repositories.basis_repository import BasisRepository

# Alle Spalten in der Reihenfolge, in der Artikel.als_datenbankwerte() liefert.
SPALTEN = (
    "kategorie, titel, beschreibung, preis, rabattsatz, "
    "lagerbestand, erstellungsdatum, aktiv, groesse, bildpfad"
)
PLATZHALTER = ", ".join("?" * 10)


class ArtikelRepository(BasisRepository):
    """Liest und schreibt Artikel."""

    tabelle = "artikel"
    schluessel = "artikel_id"

    # -- /F21/ Anlegen -----------------------------------------------------

    def speichern(self, artikel: Artikel) -> int:
        """Legt einen neuen Artikel an und gibt die vergebene ID zurueck."""
        neue_id = self.datenbank.ausfuehren(
            f"INSERT INTO artikel ({SPALTEN}) VALUES ({PLATZHALTER})",
            artikel.als_datenbankwerte(),
        )
        artikel.artikel_id = neue_id
        return neue_id

    # -- /F22/ Pflegen -----------------------------------------------------

    def aktualisieren(self, artikel: Artikel) -> None:
        """Schreibt alle Felder eines vorhandenen Artikels zurueck."""
        self.datenbank.ausfuehren(
            """UPDATE artikel SET
                   kategorie = ?, titel = ?, beschreibung = ?, preis = ?,
                   rabattsatz = ?, lagerbestand = ?, erstellungsdatum = ?,
                   aktiv = ?, groesse = ?, bildpfad = ?
               WHERE artikel_id = ?""",
            artikel.als_datenbankwerte() + (artikel.artikel_id,),
        )

    def bestand_setzen(self, artikel_id: int, neuer_bestand: int) -> None:
        """Setzt den Lagerbestand auf einen festen Wert (Inline-Bearbeitung)."""
        self.datenbank.ausfuehren(
            "UPDATE artikel SET lagerbestand = ? WHERE artikel_id = ?",
            (neuer_bestand, artikel_id),
        )

    def deaktivieren(self, artikel_id: int) -> None:
        """Soft-Delete: Artikel verschwindet aus dem Verkauf, bleibt aber in
        allen alten Bestellungen lesbar (/F22/)."""
        self.datenbank.ausfuehren(
            "UPDATE artikel SET aktiv = 0 WHERE artikel_id = ?", (artikel_id,)
        )

    def aktivieren(self, artikel_id: int) -> None:
        """Macht einen deaktivierten Artikel wieder verkaeuflich."""
        self.datenbank.ausfuehren(
            "UPDATE artikel SET aktiv = 1 WHERE artikel_id = ?", (artikel_id,)
        )

    # -- Lesen -------------------------------------------------------------

    def laden(self, artikel_id: int) -> Artikel | None:
        zeile = self.datenbank.abfragen_eine(
            "SELECT * FROM artikel WHERE artikel_id = ?", (artikel_id,)
        )
        return Artikel.aus_zeile(zeile) if zeile else None

    def alle(self, nur_aktive: bool = True) -> list[Artikel]:
        sql = "SELECT * FROM artikel"
        if nur_aktive:
            sql += " WHERE aktiv = 1"
        sql += " ORDER BY kategorie, titel"
        return [Artikel.aus_zeile(zeile) for zeile in self.datenbank.abfragen(sql)]

    # -- /F23/ Suchen und Filtern ------------------------------------------

    def suchen(
        self,
        suchtext: str = "",
        kategorie: str = "",
        min_preis: float | None = None,
        max_preis: float | None = None,
        nur_aktive: bool = True,
    ) -> list[Artikel]:
        """Kombinierte Suche ueber alle drei Filter (/F231/ bis /F233/).

        Alle Parameter sind optional und werden mit UND verknuepft. Leere
        Parameter werden einfach weggelassen - so entsteht aus einer Maske
        ohne Eingaben automatisch "zeige alles".

        * ``suchtext``  -> Volltext in Titel **und** Beschreibung (/F233/)
        * ``kategorie`` -> genau eine der sieben festen Kategorien (/F231/)
        * ``min_preis`` / ``max_preis`` -> Preisspanne (/F232/)
        """
        bedingungen: list[str] = []
        werte: list = []

        if nur_aktive:
            bedingungen.append("aktiv = 1")

        if suchtext.strip():
            bedingungen.append("(titel LIKE ? OR beschreibung LIKE ?)")
            muster = f"%{suchtext.strip()}%"
            werte.extend([muster, muster])

        if kategorie:
            bedingungen.append("kategorie = ?")
            werte.append(kategorie)

        if min_preis is not None:
            bedingungen.append("preis >= ?")
            werte.append(min_preis)

        if max_preis is not None:
            bedingungen.append("preis <= ?")
            werte.append(max_preis)

        sql = "SELECT * FROM artikel"
        if bedingungen:
            sql += " WHERE " + " AND ".join(bedingungen)
        sql += " ORDER BY titel"

        zeilen = self.datenbank.abfragen(sql, tuple(werte))
        return [Artikel.aus_zeile(zeile) for zeile in zeilen]

    # -- /F24/ und /F25/ Auswertungen --------------------------------------

    def umsatzstaerkste(self, anzahl: int = 10) -> list[dict]:
        """Artikel sortiert nach Umsatz = Menge mal gezahltem Preis (/F24/).

        Gibt Woerterbuecher zurueck und keine Artikel-Objekte, weil hier
        berechnete Werte dazukommen, die es am Artikel nicht gibt.
        """
        zeilen = self.datenbank.abfragen(
            """SELECT a.artikel_id, a.titel, a.kategorie,
                      SUM(p.menge) AS menge,
                      SUM(p.menge * p.historischer_preis) AS umsatz
               FROM bestellposition p
               JOIN artikel a ON a.artikel_id = p.artikel_id
               GROUP BY a.artikel_id
               ORDER BY umsatz DESC
               LIMIT ?""",
            (anzahl,),
        )
        return [dict(zeile) for zeile in zeilen]

    def haeufigste(self, anzahl: int = 10) -> list[dict]:
        """Artikel sortiert nach Verkaufsfrequenz (/F25/).

        Gezaehlt wird die Anzahl der **Verkaufsvorgaenge**, nicht die Stueckzahl -
        so steht der Artikel oben, der am oeftesten ueber die Theke geht.
        """
        zeilen = self.datenbank.abfragen(
            """SELECT a.artikel_id, a.titel, a.kategorie,
                      COUNT(DISTINCT p.bestellnummer) AS vorgaenge,
                      SUM(p.menge) AS menge
               FROM bestellposition p
               JOIN artikel a ON a.artikel_id = p.artikel_id
               GROUP BY a.artikel_id
               ORDER BY vorgaenge DESC, menge DESC
               LIMIT ?""",
            (anzahl,),
        )
        return [dict(zeile) for zeile in zeilen]
