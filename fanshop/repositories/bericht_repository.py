"""Datenzugriff fuer das Berichtswesen (/F31/, /F311/, /F312/, /F313/).

Alle Methoden bekommen einen Zeitraum als zwei Unix-Zeitstempel. Die Umrechnung
von Kalenderdatum zu Zeitstempel macht die Logikschicht - dieses Repository
rechnet nur.
"""

from fanshop.hilfsmittel import zeitstempel_zu_iso
from fanshop.repositories.basis_repository import BasisRepository


class BerichtRepository(BasisRepository):
    """Wertet Bewegungsdaten fuer die Geschaeftsfuehrung aus."""

    tabelle = "bestellung"
    schluessel = "bestellnummer"

    # -- /F311/ und /F312/ Kennzahlen --------------------------------------

    def kennzahlen(self, von_zeitstempel: int, bis_zeitstempel: int) -> dict:
        """Anzahl Bestellungen und Umsatz im Zeitraum.

        Zusaetzlich zum geforderten Bruttoumsatz (/F312/) werden die
        Erstattungen aus Retouren und daraus der Nettoumsatz ausgewiesen.
        Ohne diese Zeile wuerde ein Bericht Geld zeigen, das der Shop wieder
        ausgezahlt hat.
        """
        bestellungen = self.datenbank.abfragen_eine(
            """SELECT COUNT(*) AS anzahl,
                      COALESCE(SUM(gesamtbetrag), 0) AS umsatz
               FROM bestellung
               WHERE zeitstempel BETWEEN ? AND ?""",
            (von_zeitstempel, bis_zeitstempel),
        )

        # Retouren tragen ihr Datum als Text ("2026-08-20 14:03:11"). Deshalb
        # werden die Zeitraumgrenzen ebenfalls in Text umgewandelt und direkt
        # verglichen - ISO-Datumstexte sind alphabetisch sortierbar.
        retouren = self.datenbank.abfragen_eine(
            """SELECT COUNT(*) AS anzahl,
                      COALESCE(SUM(erstattungsbetrag), 0) AS betrag
               FROM retoure
               WHERE retouren_datum BETWEEN ? AND ?""",
            (zeitstempel_zu_iso(von_zeitstempel), zeitstempel_zu_iso(bis_zeitstempel)),
        )

        umsatz = bestellungen["umsatz"] if bestellungen else 0.0
        erstattungen = retouren["betrag"] if retouren else 0.0

        return {
            "anzahl_bestellungen": bestellungen["anzahl"] if bestellungen else 0,
            "umsatz": round(umsatz, 2),
            "anzahl_retouren": retouren["anzahl"] if retouren else 0,
            "erstattungen": round(erstattungen, 2),
            "nettoumsatz": round(umsatz - erstattungen, 2),
        }

    # -- /F313/ Umsatzanteile ----------------------------------------------

    def umsatzanteile(self, von_zeitstempel: int, bis_zeitstempel: int) -> list[dict]:
        """Verkaufte Artikel, sortiert nach ihrem Anteil am Gesamterloes (/F313/).

        Der prozentuale Anteil wird hier in Python ausgerechnet und nicht in
        SQL - das ist kuerzer zu lesen und vermeidet eine Division durch Null,
        wenn im Zeitraum nichts verkauft wurde.
        """
        zeilen = self.datenbank.abfragen(
            """SELECT a.artikel_id, a.titel, a.kategorie,
                      SUM(p.menge) AS menge,
                      SUM(p.menge * p.historischer_preis) AS umsatz
               FROM bestellposition p
               JOIN bestellung b ON b.bestellnummer = p.bestellnummer
               JOIN artikel a    ON a.artikel_id    = p.artikel_id
               WHERE b.zeitstempel BETWEEN ? AND ?
               GROUP BY a.artikel_id
               ORDER BY umsatz DESC""",
            (von_zeitstempel, bis_zeitstempel),
        )

        ergebnis = [dict(zeile) for zeile in zeilen]
        gesamtumsatz = sum(eintrag["umsatz"] for eintrag in ergebnis)

        for eintrag in ergebnis:
            eintrag["umsatz"] = round(eintrag["umsatz"], 2)
            eintrag["anteil"] = (
                eintrag["umsatz"] / gesamtumsatz if gesamtumsatz > 0 else 0.0
            )
        return ergebnis

    # -- Zusatz fuer die Diagramme (/F26/, /F27/) --------------------------

    def umsatz_je_kategorie(self, von_zeitstempel: int, bis_zeitstempel: int) -> list[dict]:
        """Umsatz gruppiert nach Warenkategorie - Datenbasis fuer das Balkendiagramm."""
        zeilen = self.datenbank.abfragen(
            """SELECT a.kategorie,
                      SUM(p.menge * p.historischer_preis) AS umsatz
               FROM bestellposition p
               JOIN bestellung b ON b.bestellnummer = p.bestellnummer
               JOIN artikel a    ON a.artikel_id    = p.artikel_id
               WHERE b.zeitstempel BETWEEN ? AND ?
               GROUP BY a.kategorie
               ORDER BY umsatz DESC""",
            (von_zeitstempel, bis_zeitstempel),
        )
        return [{"kategorie": z["kategorie"], "umsatz": round(z["umsatz"], 2)} for z in zeilen]

    def erste_bestellung_zeitstempel(self) -> int:
        """Zeitstempel der aeltesten Bestellung - Startpunkt fuer 'Gesamthistorie'."""
        zeile = self.datenbank.abfragen_eine(
            "SELECT MIN(zeitstempel) AS start FROM bestellung"
        )
        return zeile["start"] if zeile and zeile["start"] is not None else 0
