"""Tests für die Datenbankschicht (/NF30/)."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from fanshop.datenbank.verbindung import Datenbank, datenbank_vorbereiten

#: Das Schema, wie es vor dem Starterset-Sonderangebot aussah - Grundlage für
#: den Migrationstest. Damals durfte ein Motiv mehrfach gutgeschrieben werden.
ALTES_SCHEMA = """
CREATE TABLE kunde (
    kundennummer                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name                         TEXT    NOT NULL,
    strasse                      TEXT    NOT NULL,
    plz                          INTEGER NOT NULL,
    ort                          TEXT    NOT NULL,
    newsletter_aktiv             INTEGER NOT NULL DEFAULT 0,
    newsletter_rabatt_verfuegbar INTEGER NOT NULL DEFAULT 0,
    sticker_kontostand           INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE bestellung (
    bestellnummer                INTEGER PRIMARY KEY AUTOINCREMENT,
    kundennummer                 INTEGER,
    zeitstempel                  INTEGER NOT NULL,
    gesamtbetrag                 REAL    NOT NULL,
    newsletter_rabatt_angewendet INTEGER NOT NULL DEFAULT 0,
    sticker_ausgegeben           INTEGER NOT NULL DEFAULT 3
);
CREATE TABLE kunde_sticker (
    kundennummer INTEGER NOT NULL,
    motiv        TEXT    NOT NULL,
    anzahl       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (kundennummer, motiv)
);
"""


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

    def test_neue_spalten_sind_da(self):
        """Starterset-Spalten gehören zum Schema (/F53/)."""
        spalten = {
            zeile["name"] for zeile in self.datenbank.abfragen("PRAGMA table_info(kunde)")
        }
        self.assertIn("starterset_erhalten", spalten)

        spalten = {
            zeile["name"]
            for zeile in self.datenbank.abfragen("PRAGMA table_info(bestellung)")
        }
        self.assertIn("starterset_ausgegeben", spalten)

    def test_eigener_pfad_wird_uebernommen(self):
        datenbank = Datenbank(":memory:")
        self.assertEqual(datenbank.pfad, ":memory:")
        datenbank.schliessen()


class SchemaNachziehenTest(unittest.TestCase):
    """Eine ältere fanshop.db darf beim Start nicht kaputtgehen (/F53/).

    Wer die Anwendung schon benutzt hat, soll seine Datenbank behalten können:
    Die fehlenden Spalten kommen dazu, und der alte Sammelstand mit doppelten
    Motiven wird auf die neue Regel „jeder Sticker einmalig" umgestellt.
    """

    def setUp(self) -> None:
        self.verzeichnis = tempfile.TemporaryDirectory()
        self.pfad = Path(self.verzeichnis.name) / "alt.db"

        alt = sqlite3.connect(self.pfad)
        alt.executescript(ALTES_SCHEMA)
        alt.execute(
            """INSERT INTO kunde
                   (kundennummer, name, strasse, plz, ort, sticker_kontostand)
               VALUES (1, 'Alt Kunde', 'Weg 1', 66117, 'Saarbrücken', 9)"""
        )
        # Alter Stand: neun Sticker, drei Motive - eines davon dreifach.
        alt.executemany(
            "INSERT INTO kunde_sticker (kundennummer, motiv, anzahl) VALUES (1, ?, ?)",
            [("campus", 3), ("htwsaar", 3), ("kneipe", 3)],
        )
        alt.commit()
        alt.close()

    def tearDown(self) -> None:
        self.verzeichnis.cleanup()

    def test_fehlende_spalten_werden_ergaenzt(self):
        datenbank = datenbank_vorbereiten(self.pfad)
        try:
            kundenspalten = {
                z["name"] for z in datenbank.abfragen("PRAGMA table_info(kunde)")
            }
            bestellspalten = {
                z["name"] for z in datenbank.abfragen("PRAGMA table_info(bestellung)")
            }
            self.assertIn("starterset_erhalten", kundenspalten)
            self.assertIn("starterset_ausgegeben", bestellspalten)
        finally:
            datenbank.schliessen()

    def test_doppelte_sticker_werden_auf_einen_reduziert(self):
        datenbank = datenbank_vorbereiten(self.pfad)
        try:
            zeilen = datenbank.abfragen("SELECT anzahl FROM kunde_sticker")
            self.assertTrue(all(zeile["anzahl"] == 1 for zeile in zeilen))
        finally:
            datenbank.schliessen()

    def test_zaehler_wird_an_das_album_angeglichen(self):
        datenbank = datenbank_vorbereiten(self.pfad)
        try:
            zeile = datenbank.abfragen_eine(
                "SELECT sticker_kontostand FROM kunde WHERE kundennummer = 1"
            )
            self.assertEqual(zeile["sticker_kontostand"], 3)
        finally:
            datenbank.schliessen()

    def test_bestehende_daten_bleiben_erhalten(self):
        datenbank = datenbank_vorbereiten(self.pfad)
        try:
            zeile = datenbank.abfragen_eine("SELECT name FROM kunde WHERE kundennummer = 1")
            self.assertEqual(zeile["name"], "Alt Kunde")
        finally:
            datenbank.schliessen()

    def test_zweiter_start_aendert_nichts_mehr(self):
        datenbank_vorbereiten(self.pfad).schliessen()
        datenbank = datenbank_vorbereiten(self.pfad)
        try:
            zeile = datenbank.abfragen_eine(
                "SELECT sticker_kontostand, starterset_erhalten FROM kunde WHERE kundennummer = 1"
            )
            self.assertEqual(zeile["sticker_kontostand"], 3)
            self.assertEqual(zeile["starterset_erhalten"], 0)
        finally:
            datenbank.schliessen()


if __name__ == "__main__":
    unittest.main()
