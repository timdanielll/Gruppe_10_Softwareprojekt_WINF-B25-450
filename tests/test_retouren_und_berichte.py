"""Tests für Retouren (/F51/) und Berichtswesen (/F31/–/F313/, /F24/, /F25/)."""

import unittest

from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from tests.basis import FanshopTest


class RetourenTest(FanshopTest):

    def setUp(self) -> None:
        """Ein Kunde kauft drei Tassen - Grundlage aller Retourentests."""
        super().setUp()
        self.artikel = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=10)
        self.kunde = self.kunde_anlegen()

        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 3)
        self.beleg = self.kassen_service.kauf_abschliessen()

        # Retouren laufen ueber die Positionsnummer, nicht die Artikelnummer.
        bestellung = self.anwendung.bestell_repository.laden(self.beleg.bestellnummer)
        self.position_id = bestellung.positionen[0].position_id

    # -- /F51/ -------------------------------------------------------------

    def test_retoure_bucht_ins_lager_zurueck(self):
        """Retoure bucht ins Lager zurück."""
        bestand_vorher = self.artikel_service.laden(self.artikel.artikel_id).lagerbestand
        retoure = self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_id, 2
        )

        self.assertAlmostEqual(retoure.erstattungsbetrag, 20.00)
        self.assertEqual(
            self.artikel_service.laden(self.artikel.artikel_id).lagerbestand,
            bestand_vorher + 2,
        )

    def test_erstattung_zum_historischen_preis(self):
        """Ein späterer Preisanstieg ändert die Erstattung nicht."""
        artikel = self.artikel_service.laden(self.artikel.artikel_id)
        artikel.preis = 99.00
        self.artikel_service.aktualisieren(artikel)

        retoure = self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_id, 1
        )
        self.assertAlmostEqual(retoure.erstattungsbetrag, 10.00)

    def test_mehr_zurueckgeben_als_gekauft_wird_abgelehnt(self):
        """Mehr zurückgeben als gekauft wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.retouren_service.retoure_buchen(
                self.beleg.bestellnummer, self.position_id, 4
            )

    def test_teilretouren_summieren_sich(self):
        """Teilretouren summieren sich."""
        self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_id, 2
        )
        # Es ist nur noch 1 Stück offen.
        self.assertEqual(
            self.retouren_service.offene_menge(self.position_id, 3),
            1,
        )
        with self.assertRaises(ValidierungsFehler):
            self.retouren_service.retoure_buchen(
                self.beleg.bestellnummer, self.position_id, 2
            )

    def test_menge_null_wird_abgelehnt(self):
        """Menge Null wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.retouren_service.retoure_buchen(
                self.beleg.bestellnummer, self.position_id, 0
            )

    def test_unbekannte_bestellnummer(self):
        """Eine unbekannte Bestellnummer wird abgelehnt."""
        with self.assertRaises(NichtGefundenFehler):
            self.retouren_service.bestellung_suchen(9999)

    def test_artikel_der_nicht_in_der_bestellung_war(self):
        """Eine fremde Position wird abgelehnt."""
        anderer = self.artikel_anlegen("Poster", "Print", preis=5.00)
        with self.assertRaises(ValidierungsFehler):
            self.retouren_service.retoure_buchen(
                self.beleg.bestellnummer, anderer.artikel_id, 1
            )


class BerichteTest(FanshopTest):

    def setUp(self) -> None:
        """Legt Artikel und Kunde fuer die Auswertungen an."""
        super().setUp()
        self.tasse = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=50)
        self.stift = self.artikel_anlegen("Stift", "Schreibwaren", preis=2.00, lagerbestand=50)
        self.kunde = self.kunde_anlegen()

    def _kauf(self, artikel, menge):
        """Kauft eine Menge eines Artikels und gibt den Beleg zurueck."""
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(artikel.artikel_id, menge)
        return self.kassen_service.kauf_abschliessen()

    def _gesamtbericht(self):
        """Der Bericht ueber den kompletten Zeitraum."""
        von, bis = self.bericht_service.zeitraum_schnellwahl("gesamt")
        return self.bericht_service.bericht_erstellen(von, bis)

    # -- /F311/, /F312/ ----------------------------------------------------

    def test_anzahl_und_umsatz(self):
        """Anzahl der Bestellungen und Umsatz stimmen."""
        self._kauf(self.tasse, 2)     # 20,00
        self._kauf(self.stift, 5)     # 10,00

        bericht = self._gesamtbericht()
        self.assertEqual(bericht.anzahl_bestellungen, 2)
        self.assertAlmostEqual(bericht.umsatz, 30.00)

    def test_erstattungen_mindern_den_nettoumsatz(self):
        """Erstattungen mindern den Nettoumsatz."""
        beleg = self._kauf(self.tasse, 2)      # 20,00
        self.retouren_service.retoure_buchen(beleg.bestellnummer, self.tasse.artikel_id, 1)

        bericht = self._gesamtbericht()
        self.assertAlmostEqual(bericht.kennzahlen["erstattungen"], 10.00)
        self.assertAlmostEqual(bericht.kennzahlen["nettoumsatz"], 10.00)

    # -- /F313/ ------------------------------------------------------------

    def test_umsatzanteile_summieren_sich_auf_hundert_prozent(self):
        """Umsatzanteile summieren sich auf hundert Prozent."""
        self._kauf(self.tasse, 3)     # 30,00
        self._kauf(self.stift, 5)     # 10,00

        bericht = self._gesamtbericht()
        self.assertEqual(len(bericht.umsatzanteile), 2)
        # Der umsatzstärkste Artikel steht oben.
        self.assertEqual(bericht.umsatzanteile[0]["titel"], "Tasse")
        self.assertAlmostEqual(bericht.umsatzanteile[0]["anteil"], 0.75)
        self.assertAlmostEqual(sum(e["anteil"] for e in bericht.umsatzanteile), 1.0)

    def test_leerer_zeitraum(self):
        """Leerer Zeitraum."""
        bericht = self._gesamtbericht()
        self.assertTrue(bericht.ist_leer)
        self.assertAlmostEqual(bericht.umsatz, 0.0)
        self.assertEqual(bericht.umsatzanteile, [])

    def test_umgekehrter_zeitraum_wird_abgelehnt(self):
        """Umgekehrter Zeitraum wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.bericht_service.zeitraum_aus_datum("2026-08-20", "2026-08-01")

    def test_ungueltiges_datum_wird_abgelehnt(self):
        """Ungültiges Datum wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.bericht_service.zeitraum_aus_datum("20.08.2026", "2026-08-21")

    # -- /F24/, /F25/ ------------------------------------------------------

    def test_umsatzstaerkste_und_haeufigste_unterscheiden_sich(self):
        """Der Stift wird öfter gekauft, die Tasse bringt mehr Umsatz."""
        self._kauf(self.tasse, 3)     # 30,00, 1 Vorgang
        self._kauf(self.stift, 1)     #  2,00
        self._kauf(self.stift, 1)     #  2,00, zusammen 2 Vorgänge

        umsatz = self.artikel_service.umsatzstaerkste(5)
        haeufig = self.artikel_service.haeufigste(5)

        self.assertEqual(umsatz[0]["titel"], "Tasse")
        self.assertEqual(haeufig[0]["titel"], "Stift")
        self.assertEqual(haeufig[0]["vorgaenge"], 2)


if __name__ == "__main__":
    unittest.main()
