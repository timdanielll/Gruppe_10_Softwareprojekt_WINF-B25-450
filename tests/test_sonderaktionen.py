"""Tests für Sonderaktionen (Lastenheft: „die aktiviert werden können")."""

import unittest

from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle.sonderaktion import Sonderaktion
from tests.basis import FanshopTest


class SonderaktionModellTest(unittest.TestCase):

    def test_rabattsatz_ueber_100_prozent_wird_abgelehnt(self):
        """Sonst könnte eine Aktion den Gesamtbetrag negativ machen."""
        with self.assertRaises(ValidierungsFehler):
            Sonderaktion(titel="Kaputt", art="mindestwert", rabattsatz=1.5)

    def test_negativer_rabattsatz_wird_abgelehnt(self):
        """Negativer Rabattsatz wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            Sonderaktion(titel="Kaputt", art="mindestwert", rabattsatz=-0.1)

    def test_null_prozent_ist_erlaubt(self):
        """Null Prozent ist erlaubt."""
        aktion = Sonderaktion(titel="Ohne Rabatt", art="mindestwert", rabattsatz=0.0)
        self.assertEqual(aktion.rabattsatz, 0.0)


class SonderaktionServiceTest(FanshopTest):

    def setUp(self) -> None:
        """Legt zwei Sonderaktionen an, beide zunaechst inaktiv."""
        super().setUp()
        self.erste = self.sonderaktion_anlegen(
            titel="20 % auf Schreibwaren", zielkategorie="Schreibwaren", aktiv=False
        )
        self.zweite = self.sonderaktion_anlegen(
            titel="10 % ab 50 Euro",
            art="mindestwert",
            zielkategorie=None,
            mindestbestellwert=50.0,
            rabattsatz=0.10,
            aktiv=False,
        )
        self.dienst = self.anwendung.sonderaktion_service

    def test_alle_aktionen_werden_gelistet(self):
        """Alle Aktionen werden gelistet."""
        self.assertEqual(len(self.dienst.alle()), 2)

    def test_ohne_aktivierung_laeuft_nichts(self):
        """Ohne Aktivierung läuft nichts."""
        self.assertIsNone(self.dienst.aktive())

    def test_aktivieren_setzt_genau_eine_aktion(self):
        """Aktivieren setzt genau eine Aktion."""
        self.dienst.aktivieren(self.erste.aktions_id)
        aktive = self.dienst.aktive()

        self.assertIsNotNone(aktive)
        self.assertEqual(aktive.aktions_id, self.erste.aktions_id)
        self.assertEqual(sum(1 for a in self.dienst.alle() if a.aktiv), 1)

    def test_zweite_aktivierung_loest_die_erste_ab(self):
        """Es darf nie mehr als eine Aktion gleichzeitig laufen."""
        self.dienst.aktivieren(self.erste.aktions_id)
        self.dienst.aktivieren(self.zweite.aktions_id)

        self.assertEqual(self.dienst.aktive().aktions_id, self.zweite.aktions_id)
        self.assertEqual(sum(1 for a in self.dienst.alle() if a.aktiv), 1)

    def test_beenden_schaltet_alles_ab(self):
        """Beenden schaltet alles ab."""
        self.dienst.aktivieren(self.erste.aktions_id)
        self.dienst.beenden()
        self.assertIsNone(self.dienst.aktive())

    def test_unbekannte_aktion(self):
        """Eine unbekannte Aktionsnummer wird abgelehnt."""
        with self.assertRaises(NichtGefundenFehler):
            self.dienst.aktivieren(9999)

    def test_aktivierung_wirkt_sofort_an_der_kasse(self):
        """Der Kassen-Service liest die Aktion bei jeder Preisberechnung neu."""
        artikel = self.artikel_anlegen("Stift", "Schreibwaren", preis=10.00, lagerbestand=10)
        self.kassen_service.artikel_hinzufuegen(artikel.artikel_id, 1)

        self.assertAlmostEqual(self.kassen_service.preisuebersicht().gesamtbetrag, 10.00)

        self.dienst.aktivieren(self.erste.aktions_id)
        self.assertAlmostEqual(self.kassen_service.preisuebersicht().gesamtbetrag, 8.00)

        self.dienst.beenden()
        self.assertAlmostEqual(self.kassen_service.preisuebersicht().gesamtbetrag, 10.00)


if __name__ == "__main__":
    unittest.main()
