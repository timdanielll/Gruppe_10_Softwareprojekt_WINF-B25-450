"""Tests für den Kassiervorgang (/F14/, /F52/, /F53/)."""

import unittest

from fanshop import konfiguration
from fanshop.fehler import BestandsFehler, NichtGefundenFehler, ValidierungsFehler
from tests.basis import FanshopTest


class KassenTest(FanshopTest):

    def setUp(self) -> None:
        super().setUp()
        self.tasse = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=5)
        self.kunde = self.kunde_anlegen("Anna Becker")

    # -- /F14/ Kauf abschliessen -------------------------------------------

    def test_kauf_erzeugt_bestellung_und_bucht_lager_ab(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 2)

        beleg = self.kassen_service.kauf_abschliessen()

        self.assertIsNotNone(beleg.bestellnummer)
        self.assertAlmostEqual(beleg.uebersicht.gesamtbetrag, 20.00)
        # Lagerbestand: 5 - 2 = 3 (Mitnahmemodus)
        self.assertEqual(self.artikel_service.laden(self.tasse.artikel_id).lagerbestand, 3)

    def test_warenkorb_ist_nach_dem_kauf_leer(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)
        self.kassen_service.kauf_abschliessen()
        self.assertTrue(self.kassen_service.warenkorb.ist_leer)

    def test_leerer_warenkorb_kann_nicht_gebucht_werden(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        with self.assertRaises(ValidierungsFehler):
            self.kassen_service.kauf_abschliessen()

    def test_unbekannter_artikel(self):
        with self.assertRaises(NichtGefundenFehler):
            self.kassen_service.artikel_hinzufuegen(9999, 1)

    def test_deaktivierter_artikel_kommt_nicht_in_den_korb(self):
        self.artikel_service.deaktivieren(self.tasse.artikel_id)
        with self.assertRaises(ValidierungsFehler):
            self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)

    def test_bestand_wird_vor_dem_buchen_erneut_geprueft(self):
        """Zwischen „in den Korb" und „kassieren" kann sich der Bestand ändern."""
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 5)
        # Jemand anderes ändert währenddessen den Lagerbestand.
        self.artikel_service.bestand_setzen(self.tasse.artikel_id, 2)
        with self.assertRaises(BestandsFehler):
            self.kassen_service.kauf_abschliessen()

    # -- /F53/ Sticker -----------------------------------------------------

    def test_sticker_werden_gutgeschrieben(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.assertEqual(beleg.sticker, konfiguration.STICKER_PRO_EINKAUF)
        kunde = self.kunden_service.laden(self.kunde.kundennummer)
        self.assertEqual(kunde.sticker_kontostand, konfiguration.STICKER_PRO_EINKAUF)

    def test_laufkundschaft_bekommt_keine_sticker(self):
        self.kassen_service.kunde_abwaehlen()
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()
        self.assertEqual(beleg.sticker, 0)

    # -- /F52/ Newsletter-Gutschein ----------------------------------------

    def test_newsletter_rabatt_wird_einmal_gewaehrt(self):
        kunde = self.kunde_anlegen("Clara Schmitt", newsletter=True)
        self.kassen_service.kunde_waehlen(kunde.kundennummer)
        self.assertTrue(self.kassen_service.newsletter_rabatt_moeglich())

        self.kassen_service.newsletter_rabatt_setzen(True)
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.assertAlmostEqual(beleg.uebersicht.gesamtbetrag, 9.00)
        # Danach ist der Gutschein verbraucht.
        self.assertFalse(
            self.kunden_service.laden(kunde.kundennummer).newsletter_rabatt_verfuegbar
        )
        self.assertFalse(self.kassen_service.newsletter_rabatt_moeglich())

    def test_ohne_gutschein_kein_newsletter_rabatt(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        with self.assertRaises(ValidierungsFehler):
            self.kassen_service.newsletter_rabatt_setzen(True)

    # -- gespeicherter Einzelpreis ------------------------------------------

    def test_historischer_preis_enthaelt_den_gezahlten_betrag(self):
        """Warenkorbrabatte werden auf die Positionen verteilt.

        Sonst würde eine Retoure mehr erstatten, als der Kunde gezahlt hat.
        """
        kunde = self.kunde_anlegen("Ben Hoffmann", newsletter=True)
        self.kassen_service.kunde_waehlen(kunde.kundennummer)
        self.kassen_service.newsletter_rabatt_setzen(True)
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 2)
        beleg = self.kassen_service.kauf_abschliessen()

        positionen = self.anwendung.bestell_repository.positionen_zu(beleg.bestellnummer)
        # 10,00 abzüglich 10 % Newsletter = 9,00 pro Stück
        self.assertAlmostEqual(positionen[0].historischer_preis, 9.00)
        self.assertAlmostEqual(
            sum(p.zeilensumme for p in positionen), beleg.uebersicht.gesamtbetrag
        )


if __name__ == "__main__":
    unittest.main()
