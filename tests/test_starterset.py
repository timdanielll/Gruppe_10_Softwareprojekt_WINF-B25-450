"""Tests für das Starterset-Sonderangebot (/F53/).

Die Regel: Wer drei Einkäufe getätigt und damit alle sechs Stickermotive
gesammelt hat, bekommt einmalig Stift, Block und Jutebeutel gratis dazu.
"""

import unittest

from fanshop import konfiguration
from fanshop.modelle import starterset, sticker
from tests.basis import FanshopTest

VOLLES_ALBUM = {motiv.schluessel: 1 for motiv in sticker.MOTIVE}
HALBES_ALBUM = {motiv.schluessel: 1 for motiv in sticker.MOTIVE[:3]}


class StartersetRegelTest(unittest.TestCase):
    """Die Anspruchsregel rechnet nur - dafür braucht es keine Datenbank."""

    def test_inhalt_ist_stift_block_jutebeutel(self):
        """Das Set enthält Stift, Block und Jutebeutel."""
        self.assertEqual(starterset.INHALT, ("Stift", "Block", "Jutebeutel"))
        self.assertEqual(starterset.inhalt_text(), "Stift, Block und Jutebeutel")

    def test_anspruch_bei_drei_kaeufen_und_vollem_album(self):
        """Anspruch bei drei Käufen und vollem Album."""
        self.assertTrue(starterset.anspruch_besteht(3, VOLLES_ALBUM))

    def test_kein_anspruch_bei_zu_wenigen_kaeufen(self):
        """Kein Anspruch bei zu wenigen Käufen."""
        self.assertFalse(starterset.anspruch_besteht(2, VOLLES_ALBUM))

    def test_kein_anspruch_bei_unvollstaendigem_album(self):
        """Kein Anspruch bei unvollständigem Album."""
        self.assertFalse(starterset.anspruch_besteht(5, HALBES_ALBUM))

    def test_kein_zweites_set(self):
        """Ein zweites Starterset gibt es nicht."""
        self.assertFalse(
            starterset.anspruch_besteht(9, VOLLES_ALBUM, bereits_erhalten=True)
        )

    def test_fehlende_bestellungen(self):
        """Die Zahl der noch fehlenden Einkäufe stimmt."""
        self.assertEqual(starterset.fehlende_bestellungen(0), 3)
        self.assertEqual(starterset.fehlende_bestellungen(2), 1)
        self.assertEqual(starterset.fehlende_bestellungen(3), 0)
        self.assertEqual(starterset.fehlende_bestellungen(7), 0)

    def test_bedingung_und_mindestbestellungen_passen_zur_konfiguration(self):
        """Bedingung und Mindestbestellungen passen zur Konfiguration."""
        self.assertEqual(
            starterset.MINDESTBESTELLUNGEN, konfiguration.STARTERSET_MINDESTBESTELLUNGEN
        )
        # Drei Einkäufe à zwei Sticker ergeben genau die sechs Motive.
        self.assertEqual(
            starterset.MINDESTBESTELLUNGEN * konfiguration.STICKER_PRO_EINKAUF,
            len(sticker.MOTIVE),
        )


class StartersetAmKassenplatzTest(FanshopTest):
    """Das Set wird beim Kauf gebucht - in derselben Transaktion (/NF30/)."""

    def setUp(self) -> None:
        """Ein Kunde und ein gut bestueckter Artikel."""
        super().setUp()
        self.artikel = self.artikel_anlegen(lagerbestand=99)
        self.kunde = self.kunde_anlegen()

    def _kaufen(self, menge: int = 1):
        """Kauft einmal ein und gibt den Kaufbeleg zurueck."""
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, menge)
        return self.kassen_service.kauf_abschliessen()

    def test_die_ersten_zwei_kaeufe_bringen_kein_set(self):
        """Die ersten zwei Käufe bringen kein Set."""
        self.assertFalse(self._kaufen().starterset)
        self.assertFalse(self._kaufen().starterset)

    def test_dritter_kauf_bringt_das_set(self):
        """Dritter Kauf bringt das Set."""
        self._kaufen()
        self._kaufen()
        beleg = self._kaufen()

        self.assertTrue(beleg.starterset)
        self.assertEqual(beleg.starterset_inhalt, ("Stift", "Block", "Jutebeutel"))
        self.assertEqual(beleg.album_stand, (6, 6))

    def test_set_wird_dem_kundenkonto_gutgeschrieben(self):
        """Set wird dem Kundenkonto gutgeschrieben."""
        for _ in range(3):
            self._kaufen()

        kunde = self.kunden_service.laden(self.kunde.kundennummer)
        self.assertTrue(kunde.starterset_erhalten)
        self.assertTrue(kunde.sammlung_vollstaendig)

    def test_set_liegt_der_bestellung_bei(self):
        """Die Bestellung hält fest, welchem Kauf das Set beilag."""
        self._kaufen()
        self._kaufen()
        beleg = self._kaufen()

        bestellung = self.anwendung.bestell_repository.laden(beleg.bestellnummer)
        self.assertTrue(bestellung.starterset_ausgegeben)

    def test_es_gibt_das_set_nur_einmal(self):
        """Es gibt das Set nur einmal."""
        for _ in range(3):
            self._kaufen()
        weitere = [self._kaufen() for _ in range(3)]

        self.assertFalse(any(beleg.starterset for beleg in weitere))

        zeile = self.anwendung.datenbank.abfragen_eine(
            """SELECT COUNT(*) AS n FROM bestellung
               WHERE kundennummer = ? AND starterset_ausgegeben = 1""",
            (self.kunde.kundennummer,),
        )
        self.assertEqual(zeile["n"], 1)

    def test_laufkundschaft_bekommt_kein_set(self):
        """Laufkundschaft bekommt kein Set."""
        for _ in range(3):
            self.kassen_service.kunde_abwaehlen()
            self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
            beleg = self.kassen_service.kauf_abschliessen()

        self.assertFalse(beleg.starterset)
        self.assertEqual(beleg.starterset_inhalt, ())

    def test_kein_mindestbestellwert(self):
        """Drei Cent-Käufe reichen - es zählt allein die Zahl der Einkäufe."""
        billig = self.artikel_anlegen("Aufkleber", preis=0.01, lagerbestand=10)
        for nummer in range(3):
            self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
            self.kassen_service.artikel_hinzufuegen(billig.artikel_id, 1)
            beleg = self.kassen_service.kauf_abschliessen()

        self.assertTrue(beleg.starterset)

    def test_zwei_kunden_bekommen_jeder_ihr_set(self):
        """Die Sperre gilt je Kunde, nicht global."""
        zweiter = self.kunde_anlegen(name="Ben Hoffmann")

        for _ in range(3):
            self._kaufen()
        for _ in range(3):
            self.kassen_service.kunde_waehlen(zweiter.kundennummer)
            self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
            beleg = self.kassen_service.kauf_abschliessen()

        self.assertTrue(beleg.starterset)
        self.assertTrue(self.kunden_service.laden(zweiter.kundennummer).starterset_erhalten)

    def test_vorschau_meldet_den_faelligen_kauf(self):
        """Die Kasse kann vor dem Buchen ankündigen, dass das Set fällig ist."""
        self._kaufen()
        self._kaufen()

        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        erhalten, faellig = self.kassen_service.starterset_vorschau()

        self.assertFalse(erhalten)
        self.assertTrue(faellig)

    def test_vorschau_nach_dem_set(self):
        """Nach dem Starterset meldet die Vorschau nichts mehr."""
        for _ in range(3):
            self._kaufen()

        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        erhalten, faellig = self.kassen_service.starterset_vorschau()

        self.assertTrue(erhalten)
        self.assertFalse(faellig)

    def test_vorschau_ohne_kunden(self):
        """Vorschau ohne Kunden."""
        self.kassen_service.kunde_abwaehlen()
        self.assertEqual(self.kassen_service.starterset_vorschau(), (False, False))


class StartersetInDerKarteiTest(FanshopTest):
    """Der Stand, den die Kundenkartei anzeigt."""

    def setUp(self) -> None:
        """Ein Kunde und ein gut bestueckter Artikel."""
        super().setUp()
        self.artikel = self.artikel_anlegen(lagerbestand=99)
        self.kunde = self.kunde_anlegen()

    def _kaufen(self):
        """Kauft einmal ein und gibt den Kaufbeleg zurueck."""
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        return self.kassen_service.kauf_abschliessen()

    def test_neuer_kunde_hat_nichts(self):
        """Ein neuer Kunde hat weder Sticker noch Starterset."""
        stand = self.kunden_service.starterset_stand(self.kunde.kundennummer)

        self.assertFalse(stand.erhalten)
        self.assertFalse(stand.sammlung_vollstaendig)
        self.assertEqual(stand.anzahl_bestellungen, 0)
        self.assertEqual(stand.fehlende_bestellungen, 3)
        self.assertFalse(stand.anspruch_offen)

    def test_stand_nach_einem_kauf(self):
        """Stand nach einem Kauf."""
        self._kaufen()
        stand = self.kunden_service.starterset_stand(self.kunde.kundennummer)

        self.assertEqual(stand.anzahl_bestellungen, 1)
        self.assertEqual(stand.fehlende_bestellungen, 2)
        self.assertFalse(stand.sammlung_vollstaendig)

    def test_stand_nach_drei_kaeufen(self):
        """Stand nach drei Käufen."""
        for _ in range(3):
            self._kaufen()
        stand = self.kunden_service.starterset_stand(self.kunde.kundennummer)

        self.assertTrue(stand.erhalten)
        self.assertTrue(stand.sammlung_vollstaendig)
        self.assertEqual(stand.fehlende_bestellungen, 0)
        # Erhalten heisst: nichts mehr offen.
        self.assertFalse(stand.anspruch_offen)


class StartersetInDenTestdatenTest(unittest.TestCase):
    """Beim allerersten Start soll das Sonderangebot schon zu sehen sein."""

    def setUp(self) -> None:
        """Startet einen Beispielshop mit Testdaten."""
        from fanshop.logik.anwendung import Anwendung

        self.anwendung = Anwendung(datenbank_pfad=":memory:", testdaten=True)

    def tearDown(self) -> None:
        """Schliesst die Testdatenbank."""
        self.anwendung.schliessen()

    def test_genau_ein_kunde_hat_das_set(self):
        """In den Testdaten hat genau ein Kunde das Starterset."""
        zeile = self.anwendung.datenbank.abfragen_eine(
            "SELECT COUNT(*) AS n FROM kunde WHERE starterset_erhalten = 1"
        )
        self.assertEqual(zeile["n"], 1)

    def test_dieser_kunde_hat_ein_volles_album(self):
        """Dieser Kunde hat ein volles Album."""
        zeile = self.anwendung.datenbank.abfragen_eine(
            "SELECT kundennummer FROM kunde WHERE starterset_erhalten = 1"
        )
        album = self.anwendung.kunden_service.sticker_album(zeile["kundennummer"])

        self.assertTrue(sticker.album_vollstaendig(album))
        self.assertTrue(all(anzahl == 1 for anzahl in album.values()))

    def test_kein_testkunde_hat_ein_motiv_doppelt(self):
        """Kein testkunde hat ein Motiv doppelt."""
        zeile = self.anwendung.datenbank.abfragen_eine(
            "SELECT COALESCE(MAX(anzahl), 0) AS groesste FROM kunde_sticker"
        )
        self.assertLessEqual(zeile["groesste"], 1)

    def test_zaehler_und_album_passen_zusammen(self):
        """Zähler und Album passen zusammen."""
        for kunde in self.anwendung.kunden_service.alle():
            album = self.anwendung.kunden_service.sticker_album(kunde.kundennummer)
            self.assertEqual(
                kunde.sticker_kontostand,
                sum(album.values()),
                f"Zähler und Album weichen ab bei {kunde.name}",
            )


if __name__ == "__main__":
    unittest.main()
