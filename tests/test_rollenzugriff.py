"""Tests für die Rollenauswahl der Oberfläche."""

import unittest

from fanshop.zugriff import erlaubte_seiten


class RollenzugriffTest(unittest.TestCase):
    def test_kunde_darf_nur_die_kasse_oeffnen(self) -> None:
        self.assertEqual(erlaubte_seiten("kunde"), ("kasse",))

    def test_kassierer_darf_alle_bereiche_oeffnen(self) -> None:
        self.assertEqual(
            erlaubte_seiten("kassierer"),
            ("kasse", "artikel", "kunden", "retouren", "berichte"),
        )

    def test_unbekannte_rolle_wird_abgewiesen(self) -> None:
        with self.assertRaises(ValueError):
            erlaubte_seiten("leitung")
