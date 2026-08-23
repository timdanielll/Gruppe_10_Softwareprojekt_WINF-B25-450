"""Tests für das Sticker-Sammelsystem (/F53/)."""

import unittest

from fanshop import konfiguration
from fanshop.modelle import sticker
from tests.basis import FanshopTest


class MotivvergabeTest(unittest.TestCase):
    """Die Vergabe rechnet nur - dafür braucht es keine Datenbank."""

    def test_drei_verschiedene_motive_pro_kauf(self):
        motive = sticker.motive_fuer_kauf(0)
        self.assertEqual(len(motive), konfiguration.STICKER_PRO_EINKAUF)
        self.assertEqual(len({m.schluessel for m in motive}), 3)

    def test_zweiter_kauf_bringt_die_anderen_motive(self):
        """Nach zwei Einkäufen ist das Album genau einmal komplett."""
        erste = sticker.motive_fuer_kauf(0)
        zweite = sticker.motive_fuer_kauf(3)
        alle = {m.schluessel for m in erste} | {m.schluessel for m in zweite}
        self.assertEqual(len(alle), len(sticker.MOTIVE))

    def test_vergabe_laeuft_im_kreis(self):
        """Wer sechs Sticker hat, faengt wieder beim ersten Motiv an."""
        self.assertEqual(
            [m.schluessel for m in sticker.motive_fuer_kauf(0)],
            [m.schluessel for m in sticker.motive_fuer_kauf(len(sticker.MOTIVE))],
        )

    def test_vergabe_ist_wiederholbar(self):
        """Kein Zufall - sonst waeren die Tests unzuverlaessig."""
        self.assertEqual(
            [m.schluessel for m in sticker.motive_fuer_kauf(4)],
            [m.schluessel for m in sticker.motive_fuer_kauf(4)],
        )

    def test_jedes_motiv_hat_eine_bilddatei(self):
        for motiv in sticker.MOTIVE:
            self.assertTrue(motiv.pfad.exists(), f"Bild fehlt: {motiv.pfad}")

    def test_fortschritt_zaehlt_verschiedene_motive(self):
        self.assertEqual(sticker.album_fortschritt({}), (0, 6))
        self.assertEqual(sticker.album_fortschritt({"campus": 3}), (1, 6))
        self.assertEqual(
            sticker.album_fortschritt({m.schluessel: 1 for m in sticker.MOTIVE}), (6, 6)
        )


class AlbumTest(FanshopTest):
    """Das Album wird beim Kauf mitgeschrieben."""

    def setUp(self) -> None:
        super().setUp()
        self.artikel = self.artikel_anlegen(lagerbestand=50)
        self.kunde = self.kunde_anlegen()

    def _kaufen(self):
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        return self.kassen_service.kauf_abschliessen()

    def test_kauf_fuellt_das_album(self):
        beleg = self._kaufen()
        album = self.kunden_service.sticker_album(self.kunde.kundennummer)

        self.assertEqual(len(beleg.motive), 3)
        self.assertEqual(sum(album.values()), 3)
        self.assertEqual(beleg.album_stand, (3, 6))

    def test_zwei_kaeufe_vervollstaendigen_das_album(self):
        self._kaufen()
        beleg = self._kaufen()

        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(len(album), 6)
        self.assertEqual(beleg.album_stand, (6, 6))

    def test_doppelte_motive_erhoehen_die_anzahl(self):
        """Ab dem dritten Kauf gibt es Motive ein zweites Mal."""
        for _ in range(3):
            self._kaufen()

        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(sum(album.values()), 9)
        self.assertTrue(any(anzahl > 1 for anzahl in album.values()))

    def test_zaehler_und_album_bleiben_gleich(self):
        """sticker_kontostand muss immer der Summe im Album entsprechen."""
        for _ in range(3):
            self._kaufen()

        kunde = self.kunden_service.laden(self.kunde.kundennummer)
        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(kunde.sticker_kontostand, sum(album.values()))

    def test_laufkundschaft_bekommt_kein_album(self):
        self.kassen_service.kunde_abwaehlen()
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.assertEqual(beleg.motive, [])
        self.assertIsNone(beleg.album_stand)

    def test_album_verschwindet_mit_dem_kunden(self):
        """Loeschen des Kunden raeumt das Album mit ab (ON DELETE CASCADE)."""
        self._kaufen()
        self.kunden_service.loeschen(self.kunde.kundennummer)

        zeile = self.anwendung.datenbank.abfragen_eine(
            "SELECT COUNT(*) AS n FROM kunde_sticker WHERE kundennummer = ?",
            (self.kunde.kundennummer,),
        )
        self.assertEqual(zeile["n"], 0)


if __name__ == "__main__":
    unittest.main()
