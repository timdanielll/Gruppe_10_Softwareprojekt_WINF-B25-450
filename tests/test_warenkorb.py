"""Tests für Warenkorb und Preisberechnung (/F11/, /F12/, /F13/)."""

import unittest

from fanshop.fehler import BestandsFehler, ValidierungsFehler
from fanshop.modelle.warenkorb import Warenkorb
from tests.basis import FanshopTest


class WarenkorbTest(FanshopTest):
    """Der Warenkorb rechnet ohne Datenbank - er bekommt fertige Artikel."""

    def setUp(self) -> None:
        """Ein leerer Warenkorb, eine Tasse und ein Stift."""
        super().setUp()
        self.warenkorb = Warenkorb()
        self.tasse = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=5)
        self.stift = self.artikel_anlegen(
            "Kugelschreiber", "Schreibwaren", preis=2.00, lagerbestand=100
        )

    # -- /F11/ Hinzufuegen -------------------------------------------------

    def test_artikel_hinzufuegen(self):
        """Ein Artikel landet als Position im Warenkorb."""
        self.warenkorb.hinzufuegen(self.tasse, 2)
        self.assertEqual(len(self.warenkorb.positionen), 1)
        self.assertEqual(self.warenkorb.stueckzahl, 2)

    def test_gleicher_artikel_erhoeht_die_menge(self):
        """Zweimal derselbe Artikel ergibt eine Position mit Menge 3."""
        self.warenkorb.hinzufuegen(self.tasse, 1)
        self.warenkorb.hinzufuegen(self.tasse, 2)
        self.assertEqual(len(self.warenkorb.positionen), 1)
        self.assertEqual(self.warenkorb.positionen[0].menge, 3)

    def test_menge_null_wird_abgelehnt(self):
        """Menge Null wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.warenkorb.hinzufuegen(self.tasse, 0)

    def test_mehr_als_lagerbestand_wird_abgelehnt(self):
        """Der Lagerbestand wird vor dem Hinzufügen geprüft (/F11/)."""
        with self.assertRaises(BestandsFehler):
            self.warenkorb.hinzufuegen(self.tasse, 6)

    def test_lagerbestand_gilt_auch_kumuliert(self):
        """Zwei einzelne Zugaben dürfen den Bestand zusammen nicht sprengen."""
        self.warenkorb.hinzufuegen(self.tasse, 4)
        with self.assertRaises(BestandsFehler):
            self.warenkorb.hinzufuegen(self.tasse, 2)

    # -- /F12/ Entfernen und Menge aendern ---------------------------------

    def test_position_entfernen(self):
        """Eine Position lässt sich wieder aus dem Warenkorb nehmen."""
        self.warenkorb.hinzufuegen(self.tasse, 2)
        self.warenkorb.entfernen(self.warenkorb.positionen[0].schluessel)
        self.assertTrue(self.warenkorb.ist_leer)

    def test_menge_auf_null_entfernt_die_position(self):
        """Menge auf Null entfernt die Position."""
        self.warenkorb.hinzufuegen(self.tasse, 2)
        self.warenkorb.menge_setzen(self.warenkorb.positionen[0].schluessel, 0)
        self.assertTrue(self.warenkorb.ist_leer)

    # -- /F13/ Preisberechnung ---------------------------------------------

    def test_summe_ohne_rabatt(self):
        """Summe ohne Rabatt."""
        self.warenkorb.hinzufuegen(self.tasse, 2)      # 2 x 10,00
        self.warenkorb.hinzufuegen(self.stift, 3)      # 3 x  2,00
        uebersicht = self.warenkorb.berechne()
        self.assertAlmostEqual(uebersicht.listenwert, 26.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 26.00)

    def test_artikelrabatt_wird_abgezogen(self):
        """Artikelrabatt wird abgezogen."""
        rabattartikel = self.artikel_anlegen(
            "Hoodie", "Herren", preis=40.00, lagerbestand=5, rabattsatz=0.25
        )
        self.warenkorb.hinzufuegen(rabattartikel, 1, "L")
        uebersicht = self.warenkorb.berechne()
        self.assertAlmostEqual(uebersicht.listenwert, 40.00)
        self.assertAlmostEqual(uebersicht.artikelrabatt, 10.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 30.00)

    def test_sonderaktion_auf_kategorie(self):
        """20 % auf Schreibwaren wirken nur auf die Schreibwaren-Position."""
        aktion = self.sonderaktion_anlegen(
            art="kategorie", zielkategorie="Schreibwaren", rabattsatz=0.20
        )
        self.warenkorb.hinzufuegen(self.tasse, 1)      # 10,00 - nicht betroffen
        self.warenkorb.hinzufuegen(self.stift, 5)      # 10,00 - betroffen
        uebersicht = self.warenkorb.berechne(sonderaktion=aktion)
        self.assertAlmostEqual(uebersicht.aktionsrabatt, 2.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 18.00)

    def test_sonderaktion_ab_mindestbestellwert(self):
        """Sonderaktion ab Mindestbestellwert."""
        aktion = self.sonderaktion_anlegen(
            art="mindestwert", zielkategorie=None, mindestbestellwert=50.0, rabattsatz=0.10
        )
        self.warenkorb.hinzufuegen(self.tasse, 5)      # 50,00 -> Aktion greift
        uebersicht = self.warenkorb.berechne(sonderaktion=aktion)
        self.assertAlmostEqual(uebersicht.aktionsrabatt, 5.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 45.00)

    def test_sonderaktion_unter_mindestbestellwert_greift_nicht(self):
        """Sonderaktion unter Mindestbestellwert greift nicht."""
        aktion = self.sonderaktion_anlegen(
            art="mindestwert", zielkategorie=None, mindestbestellwert=50.0, rabattsatz=0.10
        )
        self.warenkorb.hinzufuegen(self.tasse, 2)      # nur 20,00
        uebersicht = self.warenkorb.berechne(sonderaktion=aktion)
        self.assertAlmostEqual(uebersicht.aktionsrabatt, 0.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 20.00)

    def test_inaktive_sonderaktion_wird_ignoriert(self):
        """Inaktive Sonderaktion wird ignoriert."""
        aktion = self.sonderaktion_anlegen(rabattsatz=0.50, aktiv=False)
        self.warenkorb.hinzufuegen(self.stift, 5)
        uebersicht = self.warenkorb.berechne(sonderaktion=aktion)
        self.assertAlmostEqual(uebersicht.aktionsrabatt, 0.00)

    def test_newsletter_rabatt(self):
        """Newsletter Rabatt."""
        self.warenkorb.hinzufuegen(self.tasse, 1)      # 10,00
        uebersicht = self.warenkorb.berechne(newsletter_rabatt_anwenden=True)
        self.assertAlmostEqual(uebersicht.newsletter_rabatt, 1.00)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 9.00)

    def test_alle_drei_rabatte_kumulieren_in_fester_reihenfolge(self):
        """Artikelrabatt, dann Sonderaktion, dann Newsletter (/F13/).

        Rechnung: 100,00 − 20 % Artikelrabatt = 80,00
                   80,00 − 10 % Aktion        = 72,00
                   72,00 − 10 % Newsletter    = 64,80
        """
        artikel = self.artikel_anlegen(
            "Rucksack", "Accessoires", preis=100.00, lagerbestand=3, rabattsatz=0.20
        )
        aktion = self.sonderaktion_anlegen(
            art="kategorie", zielkategorie="Accessoires", rabattsatz=0.10
        )
        self.warenkorb.hinzufuegen(artikel, 1)
        uebersicht = self.warenkorb.berechne(
            sonderaktion=aktion, newsletter_rabatt_anwenden=True
        )

        self.assertAlmostEqual(uebersicht.listenwert, 100.00)
        self.assertAlmostEqual(uebersicht.artikelrabatt, 20.00)
        self.assertAlmostEqual(uebersicht.aktionsrabatt, 8.00)
        self.assertAlmostEqual(uebersicht.newsletter_rabatt, 7.20)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 64.80)

    def test_leerer_warenkorb_kostet_nichts(self):
        """Leerer Warenkorb kostet nichts."""
        uebersicht = self.warenkorb.berechne(newsletter_rabatt_anwenden=True)
        self.assertAlmostEqual(uebersicht.gesamtbetrag, 0.00)
        self.assertAlmostEqual(uebersicht.newsletter_rabatt, 0.00)


if __name__ == "__main__":
    unittest.main()
