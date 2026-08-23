"""Tests für die Datenbankschicht (/NF30/)."""

import sqlite3
import unittest

from fanshop.datenbank.verbindung import Datenbank, datenbank_vorbereiten


class DatenbankTest(unittest.TestCase):

    def setUp(self) -> None:
        self.datenbank = datenbank_vorbereiten(":memory:")

    def tearDown(self) -> None:
        self.datenbank.schliessen()

    def test_alle_tabellen_werden_angelegt(self):
        zeilen = self.datenbank.abfragen(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
        namen = {zeile["name"] for zeile in zeilen}
        for erwartet in (
            "kunde",
            "artikel",
            "bestellung",
            "bestellposition",
            "retoure",
            "sonderaktion",
        ):
            self.assertIn(erwartet, namen)

    def test_schema_kann_mehrfach_ausgefuehrt_werden(self):
        """Ein zweiter Programmstart darf nichts löschen."""
        self.datenbank.ausfuehren(
            "INSERT INTO kunde (name, strasse, plz, ort) VALUES (?, ?, ?, ?)",
            ("Testkunde", "Weg 1", 66117, "Saarbrücken"),
        )
        self.datenbank.schema_anlegen()  # noch einmal
        zeile = self.datenbank.abfragen_eine("SELECT COUNT(*) AS n FROM kunde")
        self.assertEqual(zeile["n"], 1)

    def test_fremdschluessel_sind_eingeschaltet(self):
        zeile = self.datenbank.abfragen_eine("PRAGMA foreign_keys")
        self.assertEqual(zeile[0], 1)

    def test_transaktion_wird_bei_einem_fehler_zurueckgerollt(self):
        """Entweder alles oder nichts - das ist die Zusage aus /NF30/."""
        with self.assertRaises(sqlite3.Error):
            with self.datenbank.transaktion() as verbindung:
                verbindung.execute(
                    "INSERT INTO kunde (name, strasse, plz, ort) VALUES (?, ?, ?, ?)",
                    ("Wird verworfen", "Weg 1", 66117, "Saarbrücken"),
                )
                # Diese Anweisung scheitert -> die erste muss ebenfalls weg sein.
                verbindung.execute("INSERT INTO gibtesnicht (a) VALUES (1)")

        zeile = self.datenbank.abfragen_eine("SELECT COUNT(*) AS n FROM kunde")
        self.assertEqual(zeile["n"], 0)

    def test_zeilen_lassen_sich_wie_ein_woerterbuch_lesen(self):
        self.datenbank.ausfuehren(
            "INSERT INTO kunde (name, strasse, plz, ort) VALUES (?, ?, ?, ?)",
            ("Anna Becker", "Waldhausweg 14", 66123, "Saarbrücken"),
        )
        zeile = self.datenbank.abfragen_eine("SELECT * FROM kunde")
        self.assertEqual(zeile["name"], "Anna Becker")

    def test_eigener_pfad_wird_uebernommen(self):
        datenbank = Datenbank(":memory:")
        self.assertEqual(datenbank.pfad, ":memory:")
        datenbank.schliessen()


if __name__ == "__main__":
    unittest.main()
