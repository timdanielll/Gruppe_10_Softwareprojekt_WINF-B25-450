"""Tests für das Sticker-Sammelsystem (/F53/).

Drei Regeln stehen hier auf dem Prüfstand: zwei Sticker pro Kauf, feste
Reihenfolge, und **jedes Motiv nur einmal**.
"""

import unittest

from fanshop import konfiguration
from fanshop.modelle import sticker
from tests.basis import FanshopTest


class MotivvergabeTest(unittest.TestCase):
    """Die Vergabe rechnet nur - dafür braucht es keine Datenbank."""

    def test_zwei_verschiedene_motive_pro_kauf(self):
        """Zwei verschiedene Motive pro Kauf."""
        motive = sticker.motive_fuer_kauf(0)
        self.assertEqual(len(motive), konfiguration.STICKER_PRO_EINKAUF)
        self.assertEqual(len({m.schluessel for m in motive}), 2)

    def test_drei_kaeufe_vervollstaendigen_die_sammlung(self):
        """Nach drei Einkäufen ist das Album genau einmal komplett."""
        alle = set()
        for kontostand in (0, 2, 4):
            alle |= {m.schluessel for m in sticker.motive_fuer_kauf(kontostand)}
        self.assertEqual(len(alle), len(sticker.MOTIVE))

    def test_die_reihenfolge_bleibt_die_der_liste(self):
        """Die Reihenfolge bleibt die der Liste."""
        self.assertEqual(
            [m.schluessel for m in sticker.motive_fuer_kauf(2)],
            [sticker.MOTIVE[2].schluessel, sticker.MOTIVE[3].schluessel],
        )

    def test_volle_sammlung_bringt_keine_sticker_mehr(self):
        """Kein Motiv wird ein zweites Mal vergeben - die Vergabe läuft aus."""
        self.assertEqual(sticker.motive_fuer_kauf(len(sticker.MOTIVE)), [])
        self.assertEqual(sticker.motive_fuer_kauf(len(sticker.MOTIVE) + 5), [])

    def test_letzter_kauf_gibt_nur_noch_den_rest(self):
        """Bei fünf vorhandenen Stickern bleibt genau einer übrig."""
        self.assertEqual(len(sticker.motive_fuer_kauf(len(sticker.MOTIVE) - 1)), 1)

    def test_vergabe_ist_wiederholbar(self):
        """Kein Zufall - sonst wären die Tests unzuverlässig."""
        self.assertEqual(
            [m.schluessel for m in sticker.motive_fuer_kauf(4)],
            [m.schluessel for m in sticker.motive_fuer_kauf(4)],
        )

    def test_offene_motive_ueberspringt_vorhandene(self):
        """Die Vergabe am Kaufabschluss richtet sich nach dem Album."""
        album = {sticker.MOTIVE[0].schluessel: 1, sticker.MOTIVE[2].schluessel: 1}
        offen = sticker.offene_motive(album)

        self.assertEqual(
            [m.schluessel for m in offen],
            [sticker.MOTIVE[1].schluessel, sticker.MOTIVE[3].schluessel],
        )

    def test_offene_motive_ist_leer_bei_vollem_album(self):
        """Offene Motive ist leer bei vollem Album."""
        album = {m.schluessel: 1 for m in sticker.MOTIVE}
        self.assertEqual(sticker.offene_motive(album), [])

    def test_jedes_motiv_hat_eine_bilddatei(self):
        """Jedes Motiv hat eine bilddatei."""
        for motiv in sticker.MOTIVE:
            self.assertTrue(motiv.pfad.exists(), f"Bild fehlt: {motiv.pfad}")

    def test_fortschritt_zaehlt_verschiedene_motive(self):
        """Fortschritt zählt verschiedene Motive."""
        self.assertEqual(sticker.album_fortschritt({}), (0, 6))
        self.assertEqual(sticker.album_fortschritt({"campus": 1}), (1, 6))
        self.assertEqual(
            sticker.album_fortschritt({m.schluessel: 1 for m in sticker.MOTIVE}), (6, 6)
        )

    def test_vollstaendigkeit(self):
        """Vollständigkeit."""
        self.assertFalse(sticker.album_vollstaendig({"campus": 1}))
        self.assertTrue(
            sticker.album_vollstaendig({m.schluessel: 1 for m in sticker.MOTIVE})
        )


class AlbumTest(FanshopTest):
    """Das Album wird beim Kauf mitgeschrieben."""

    def setUp(self) -> None:
        """Ein Kunde und ein Artikel mit reichlich Bestand."""
        super().setUp()
        self.artikel = self.artikel_anlegen(lagerbestand=50)
        self.kunde = self.kunde_anlegen()

    def _kaufen(self):
        """Kauft einmal ein und gibt den Kaufbeleg zurueck."""
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        return self.kassen_service.kauf_abschliessen()

    def test_kauf_fuellt_das_album(self):
        """Kauf füllt das Album."""
        beleg = self._kaufen()
        album = self.kunden_service.sticker_album(self.kunde.kundennummer)

        self.assertEqual(len(beleg.motive), 2)
        self.assertEqual(sum(album.values()), 2)
        self.assertEqual(beleg.album_stand, (2, 6))

    def test_drei_kaeufe_vervollstaendigen_das_album(self):
        """Drei Käufe vervollständigen das Album."""
        for _ in range(2):
            self._kaufen()
        beleg = self._kaufen()

        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(len(album), 6)
        self.assertEqual(beleg.album_stand, (6, 6))

    def test_kein_motiv_wird_zweimal_vergeben(self):
        """Auch nach sechs Einkäufen liegt jedes Motiv genau einmal im Album."""
        for _ in range(6):
            self._kaufen()

        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(len(album), 6)
        self.assertTrue(all(anzahl == 1 for anzahl in album.values()))
        self.assertEqual(sum(album.values()), 6)

    def test_kauf_mit_vollem_album_gibt_keine_sticker(self):
        """Kauf mit vollem Album gibt keine Sticker."""
        for _ in range(3):
            self._kaufen()
        beleg = self._kaufen()

        self.assertEqual(beleg.motive, [])
        self.assertEqual(beleg.sticker, 0)
        self.assertEqual(beleg.album_stand, (6, 6))

    def test_vierter_kauf_erhoeht_den_zaehler_nicht(self):
        """Der Zähler bleibt bei sechs stehen - mehr Motive gibt es nicht."""
        for _ in range(4):
            self._kaufen()

        kunde = self.kunden_service.laden(self.kunde.kundennummer)
        self.assertEqual(kunde.sticker_kontostand, len(sticker.MOTIVE))

    def test_zaehler_und_album_bleiben_gleich(self):
        """Sticker_kontostand muss immer der Summe im Album entsprechen."""
        for _ in range(5):
            self._kaufen()

        kunde = self.kunden_service.laden(self.kunde.kundennummer)
        album = self.kunden_service.sticker_album(self.kunde.kundennummer)
        self.assertEqual(kunde.sticker_kontostand, sum(album.values()))

    def test_bestellung_merkt_sich_die_ausgegebene_anzahl(self):
        """Der Beleg hält fest, wie viele Sticker wirklich herausgingen."""
        erste = self._kaufen()
        for _ in range(2):
            self._kaufen()
        ohne = self._kaufen()

        self.assertEqual(
            self.anwendung.bestell_repository.laden(erste.bestellnummer).sticker_ausgegeben,
            2,
        )
        self.assertEqual(
            self.anwendung.bestell_repository.laden(ohne.bestellnummer).sticker_ausgegeben,
            0,
        )

    def test_laufkundschaft_bekommt_kein_album(self):
        """Laufkundschaft bekommt kein Album."""
        self.kassen_service.kunde_abwaehlen()
        self.kassen_service.artikel_hinzufuegen(self.artikel.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.assertEqual(beleg.motive, [])
        self.assertIsNone(beleg.album_stand)

    def test_kein_mindestbestellwert(self):
        """Auch ein Ein-Cent-Kauf bringt die vollen zwei Sticker."""
        billig = self.artikel_anlegen("Aufkleber", preis=0.01, lagerbestand=5)
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(billig.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.assertEqual(beleg.sticker, konfiguration.STICKER_PRO_EINKAUF)

    def test_album_verschwindet_mit_dem_kunden(self):
        """Löschen des Kunden räumt das Album mit ab (ON DELETE CASCADE)."""
        self._kaufen()
        self.kunden_service.loeschen(self.kunde.kundennummer)

        zeile = self.anwendung.datenbank.abfragen_eine(
            "SELECT COUNT(*) AS n FROM kunde_sticker WHERE kundennummer = ?",
            (self.kunde.kundennummer,),
        )
        self.assertEqual(zeile["n"], 0)


if __name__ == "__main__":
    unittest.main()
