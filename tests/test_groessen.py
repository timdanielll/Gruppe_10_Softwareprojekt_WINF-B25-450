"""Tests für die Größenauswahl beim Bestellen (/F11/, /NF20/).

Die Regeln: Jeder Artikel steht genau einmal im Sortiment, Damen und Herren
führen dieselben Textilien, und die Größe wird erst beim Bestellen gewählt —
Damen S–XL, Herren S–5XL.
"""

import json
import unittest

from fanshop import konfiguration
from fanshop.fehler import BestandsFehler, ValidierungsFehler
from fanshop.logik.anwendung import Anwendung
from fanshop.modelle.artikel import Artikel, Kleidungsartikel
from fanshop.modelle.warenkorb import Warenkorb
from tests.basis import FanshopTest


class GroessenKonfigurationTest(unittest.TestCase):
    """Die Spannen stehen an einer Stelle und gelten je Kategorie."""

    def test_damen_von_s_bis_xl(self):
        """Damen führen die Größen S bis XL."""
        self.assertEqual(konfiguration.groessen_fuer("Damen"), ("S", "M", "L", "XL"))

    def test_herren_von_s_bis_5xl(self):
        """Herren führen die Größen S bis 5XL."""
        self.assertEqual(
            konfiguration.groessen_fuer("Herren"),
            ("S", "M", "L", "XL", "XXL", "3XL", "4XL", "5XL"),
        )

    def test_andere_kategorien_haben_keine_groessen(self):
        """Andere Kategorien haben keine Größen."""
        for kategorie in ("Accessoires", "Schreibwaren", "Print", "Specials", "Tickets"):
            self.assertEqual(konfiguration.groessen_fuer(kategorie), ())

    def test_unbekannte_kategorie_ist_harmlos(self):
        """Unbekannte Kategorie ist harmlos."""
        self.assertEqual(konfiguration.groessen_fuer("Gibtsnicht"), ())

    def test_kleidungskategorien_kommen_aus_der_groessentabelle(self):
        """Kleidungskategorien kommen aus der Größentabelle."""
        self.assertEqual(
            set(konfiguration.KLEIDUNGS_KATEGORIEN),
            set(konfiguration.GROESSEN_JE_KATEGORIE),
        )

    def test_damen_ist_teilmenge_der_herren(self):
        """Damen führen dieselben Größen, nur ohne die großen Weiten."""
        self.assertTrue(
            set(konfiguration.groessen_fuer("Damen"))
            <= set(konfiguration.groessen_fuer("Herren"))
        )


class ArtikelGroessenTest(FanshopTest):
    """Die Größenspanne hängt an der Kategorie, nicht am einzelnen Artikel."""

    def test_kleidung_kennt_ihre_groessen(self):
        """Kleidung kennt ihre Größen."""
        damen = self.artikel_anlegen("Hoodie Damen", "Damen")
        herren = self.artikel_anlegen("Hoodie Herren", "Herren")

        self.assertEqual(damen.groessen, ("S", "M", "L", "XL"))
        self.assertEqual(len(herren.groessen), 8)
        self.assertTrue(damen.braucht_groesse)
        self.assertTrue(herren.braucht_groesse)

    def test_zubehoer_braucht_keine_groesse(self):
        """Zubehör braucht keine Größe."""
        tasse = self.artikel_anlegen("Tasse", "Accessoires")

        self.assertIsInstance(tasse, Artikel)
        self.assertNotIsInstance(tasse, Kleidungsartikel)
        self.assertEqual(tasse.groessen, ())
        self.assertFalse(tasse.braucht_groesse)

    def test_merkmale_nennen_die_spanne(self):
        """Die Merkmale nennen die Größenspanne."""
        herren = self.artikel_anlegen("Hoodie", "Herren")
        self.assertIn("5XL", herren.merkmale())

    def test_groesse_pruefen_nimmt_kleinschreibung_an(self):
        """Größe prüfen nimmt Kleinschreibung an."""
        herren = self.artikel_anlegen("Hoodie", "Herren")
        self.assertEqual(herren.groesse_pruefen("xxl"), "XXL")

    def test_groesse_pruefen_lehnt_unbekanntes_ab(self):
        """Größe prüfen lehnt Unbekanntes ab."""
        damen = self.artikel_anlegen("Hoodie", "Damen")
        with self.assertRaises(ValidierungsFehler):
            damen.groesse_pruefen("5XL")     # gibt es nur bei Herren

    def test_groesse_pruefen_verlangt_eine_angabe(self):
        """Größe prüfen verlangt eine Angabe."""
        damen = self.artikel_anlegen("Hoodie", "Damen")
        with self.assertRaises(ValidierungsFehler):
            damen.groesse_pruefen("")

    def test_zubehoer_ignoriert_eine_groesse(self):
        """Zubehör ignoriert eine Größe."""
        tasse = self.artikel_anlegen("Tasse", "Accessoires")
        self.assertEqual(tasse.groesse_pruefen("L"), "")


class WarenkorbGroessenTest(FanshopTest):
    """Größe gehört zur Warenkorbzeile und bestimmt ihre Identität."""

    def setUp(self) -> None:
        """Ein Herren-Hoodie und eine Tasse als Grundausstattung."""
        super().setUp()
        self.warenkorb = Warenkorb()
        self.hoodie = self.artikel_anlegen("Hoodie", "Herren", preis=40.00, lagerbestand=10)
        self.tasse = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=10)

    def test_zwei_groessen_sind_zwei_zeilen(self):
        """Zwei Größen sind zwei Zeilen."""
        self.warenkorb.hinzufuegen(self.hoodie, 1, "M")
        self.warenkorb.hinzufuegen(self.hoodie, 2, "L")

        self.assertEqual(len(self.warenkorb.positionen), 2)
        self.assertEqual(self.warenkorb.stueckzahl, 3)
        self.assertEqual(
            [p.groesse for p in self.warenkorb.positionen], ["M", "L"]
        )

    def test_gleiche_groesse_erhoeht_die_menge(self):
        """Gleiche Größe erhöht die Menge."""
        self.warenkorb.hinzufuegen(self.hoodie, 1, "M")
        self.warenkorb.hinzufuegen(self.hoodie, 2, "M")

        self.assertEqual(len(self.warenkorb.positionen), 1)
        self.assertEqual(self.warenkorb.positionen[0].menge, 3)

    def test_kleidung_ohne_groesse_wird_abgelehnt(self):
        """Kleidung ohne Größe wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.warenkorb.hinzufuegen(self.hoodie, 1)

    def test_bestand_gilt_ueber_alle_groessen(self):
        """10 auf Lager heißt 10 insgesamt, nicht 10 je Größe."""
        self.warenkorb.hinzufuegen(self.hoodie, 6, "M")
        with self.assertRaises(BestandsFehler):
            self.warenkorb.hinzufuegen(self.hoodie, 5, "L")

    def test_menge_setzen_beachtet_die_anderen_groessen(self):
        """Menge setzen beachtet die anderen Größen."""
        self.warenkorb.hinzufuegen(self.hoodie, 6, "M")
        self.warenkorb.hinzufuegen(self.hoodie, 2, "L")
        schluessel_l = self.warenkorb.position_zu(self.hoodie.artikel_id, "L").schluessel

        with self.assertRaises(BestandsFehler):
            self.warenkorb.menge_setzen(schluessel_l, 5)   # 6 + 5 > 10

        self.warenkorb.menge_setzen(schluessel_l, 4)       # 6 + 4 = 10 ist erlaubt
        self.assertEqual(self.warenkorb.stueckzahl, 10)

    def test_entfernen_trifft_nur_eine_groesse(self):
        """Entfernen trifft nur eine Größe."""
        self.warenkorb.hinzufuegen(self.hoodie, 1, "M")
        self.warenkorb.hinzufuegen(self.hoodie, 1, "L")
        schluessel_m = self.warenkorb.position_zu(self.hoodie.artikel_id, "M").schluessel

        self.warenkorb.entfernen(schluessel_m)

        self.assertEqual(len(self.warenkorb.positionen), 1)
        self.assertEqual(self.warenkorb.positionen[0].groesse, "L")

    def test_anzeigename_nennt_die_groesse(self):
        """Anzeigename nennt die Größe."""
        self.warenkorb.hinzufuegen(self.hoodie, 1, "XXL")
        self.warenkorb.hinzufuegen(self.tasse, 1)

        self.assertEqual(self.warenkorb.positionen[0].anzeigename, "Hoodie (Gr. XXL)")
        self.assertEqual(self.warenkorb.positionen[1].anzeigename, "Tasse")

    def test_schluessel_unterscheidet_die_groessen(self):
        """Schlüssel unterscheidet die Größen."""
        self.warenkorb.hinzufuegen(self.hoodie, 1, "M")
        self.warenkorb.hinzufuegen(self.hoodie, 1, "L")
        schluessel = {p.schluessel for p in self.warenkorb.positionen}
        self.assertEqual(len(schluessel), 2)


class KaufMitGroesseTest(FanshopTest):
    """Die gewählte Größe landet auf der Bestellposition."""

    def setUp(self) -> None:
        """Ein Kunde, ein Hoodie und eine Tasse."""
        super().setUp()
        self.hoodie = self.artikel_anlegen("Hoodie", "Herren", preis=40.00, lagerbestand=20)
        self.tasse = self.artikel_anlegen("Tasse", "Accessoires", preis=10.00, lagerbestand=20)
        self.kunde = self.kunde_anlegen()

    def test_groesse_wird_mitgebucht(self):
        """Größe wird mitgebucht."""
        self.kassen_service.kunde_waehlen(self.kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 1, "3XL")
        beleg = self.kassen_service.kauf_abschliessen()

        bestellung = self.anwendung.bestell_repository.laden(beleg.bestellnummer)
        self.assertEqual(bestellung.positionen[0].groesse, "3XL")
        self.assertIn("3XL", bestellung.positionen[0].anzeigename)

    def test_artikel_ohne_groesse_speichert_nichts(self):
        """Artikel ohne Größe speichert nichts."""
        self.kassen_service.artikel_hinzufuegen(self.tasse.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        bestellung = self.anwendung.bestell_repository.laden(beleg.bestellnummer)
        self.assertEqual(bestellung.positionen[0].groesse, "")

    def test_zwei_groessen_werden_zu_zwei_positionen(self):
        """Zwei Größen werden zu zwei Positionen."""
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 1, "M")
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 2, "L")
        beleg = self.kassen_service.kauf_abschliessen()

        bestellung = self.anwendung.bestell_repository.laden(beleg.bestellnummer)
        self.assertEqual(len(bestellung.positionen), 2)
        self.assertEqual(
            sorted(p.groesse for p in bestellung.positionen), ["L", "M"]
        )

    def test_lager_wird_ueber_beide_groessen_abgebucht(self):
        """Lager wird über beide Größen abgebucht."""
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 1, "M")
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 2, "L")
        self.kassen_service.kauf_abschliessen()

        self.assertEqual(
            self.artikel_service.laden(self.hoodie.artikel_id).lagerbestand, 17
        )

    def test_falsche_groesse_wird_an_der_kasse_abgelehnt(self):
        """Falsche Größe wird an der Kasse abgelehnt."""
        damen = self.artikel_anlegen("Shirt", "Damen", preis=20.00, lagerbestand=5)
        with self.assertRaises(ValidierungsFehler):
            self.kassen_service.artikel_hinzufuegen(damen.artikel_id, 1, "5XL")

    def test_groessen_fuer_liefert_die_auswahl(self):
        """Größen für liefert die Auswahl."""
        self.assertEqual(len(self.kassen_service.groessen_fuer(self.hoodie.artikel_id)), 8)
        self.assertEqual(self.kassen_service.groessen_fuer(self.tasse.artikel_id), ())
        self.assertEqual(self.kassen_service.groessen_fuer(9999), ())


class RetoureMitGroesseTest(FanshopTest):
    """Retouren treffen genau die Größe, die zurückgebracht wird."""

    def setUp(self) -> None:
        """Ein Kauf mit demselben Hoodie in zwei Größen."""
        super().setUp()
        self.hoodie = self.artikel_anlegen("Hoodie", "Herren", preis=40.00, lagerbestand=20)
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 3, "M")
        self.kassen_service.artikel_hinzufuegen(self.hoodie.artikel_id, 2, "L")
        self.beleg = self.kassen_service.kauf_abschliessen()

        bestellung = self.anwendung.bestell_repository.laden(self.beleg.bestellnummer)
        self.position_m = next(p for p in bestellung.positionen if p.groesse == "M")
        self.position_l = next(p for p in bestellung.positionen if p.groesse == "L")

    def test_retoure_belastet_nur_ihre_position(self):
        """Retoure belastet nur ihre Position."""
        self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_m.position_id, 3
        )

        # Größe M ist erschöpft, Größe L unberührt.
        self.assertEqual(self.retouren_service.offene_menge(self.position_m.position_id, 3), 0)
        self.assertEqual(self.retouren_service.offene_menge(self.position_l.position_id, 2), 2)

    def test_zweite_groesse_bleibt_zurueckgebbar(self):
        """Zweite Größe bleibt zurückgebbar."""
        self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_m.position_id, 3
        )
        retoure = self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_l.position_id, 2
        )

        self.assertEqual(retoure.groesse, "L")
        self.assertIn("Gr. L", retoure.anzeigename)

    def test_retourenbeleg_merkt_sich_die_position(self):
        """Retourenbeleg merkt sich die Position."""
        self.retouren_service.retoure_buchen(
            self.beleg.bestellnummer, self.position_l.position_id, 1
        )
        retouren = self.retouren_service.retouren_zu(self.beleg.bestellnummer)

        self.assertEqual(len(retouren), 1)
        self.assertEqual(retouren[0].position_id, self.position_l.position_id)
        self.assertEqual(retouren[0].groesse, "L")

    def test_fremde_position_wird_abgelehnt(self):
        """Fremde Position wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.retouren_service.retoure_buchen(self.beleg.bestellnummer, 9999, 1)


class SortimentTest(unittest.TestCase):
    """Jeder Artikel kommt genau einmal vor - Katalog und Datenbank."""

    def setUp(self) -> None:
        """Startet einen Beispielshop mit dem echten Katalog."""
        self.anwendung = Anwendung(datenbank_pfad=":memory:", testdaten=True)

    def tearDown(self) -> None:
        """Schliesst die Testdatenbank."""
        self.anwendung.schliessen()

    def test_katalog_hat_keine_doppelten_titel(self):
        """Katalog hat keine doppelten Titel."""
        katalog = json.loads(
            (konfiguration.ARTIKELBILDER_VERZEICHNIS / "katalog.json").read_text(
                encoding="utf-8"
            )
        )
        titel = [eintrag["titel"] for eintrag in katalog]
        self.assertEqual(len(titel), len(set(titel)))

    def test_katalog_hat_keine_doppelten_fotos(self):
        """Zwei Einträge mit demselben Bild wären zwei Ansichten eines Produkts."""
        katalog = json.loads(
            (konfiguration.ARTIKELBILDER_VERZEICHNIS / "katalog.json").read_text(
                encoding="utf-8"
            )
        )
        dateien = [eintrag["datei"] for eintrag in katalog]
        self.assertEqual(len(dateien), len(set(dateien)))

    def test_katalog_fuehrt_keine_groesse_mehr(self):
        """Katalog führt keine Größe mehr."""
        katalog = json.loads(
            (konfiguration.ARTIKELBILDER_VERZEICHNIS / "katalog.json").read_text(
                encoding="utf-8"
            )
        )
        for eintrag in katalog:
            self.assertNotIn("groesse", eintrag)

    def test_jeder_artikel_kommt_genau_einmal_vor(self):
        """Jeder Artikel kommt genau einmal vor."""
        zeile = self.anwendung.datenbank.abfragen_eine(
            """SELECT COUNT(*) AS doppelte FROM (
                   SELECT titel FROM artikel GROUP BY titel HAVING COUNT(*) > 1
               )"""
        )
        self.assertEqual(zeile["doppelte"], 0)

    def test_alle_bilder_sind_verschieden(self):
        """Kein Produktfoto wird von zwei Artikeln benutzt."""
        zeile = self.anwendung.datenbank.abfragen_eine(
            """SELECT COUNT(*) AS doppelte FROM (
                   SELECT bildpfad FROM artikel
                   WHERE bildpfad IS NOT NULL
                   GROUP BY bildpfad HAVING COUNT(*) > 1
               )"""
        )
        self.assertEqual(zeile["doppelte"], 0)

    def test_damen_und_herren_fuehren_dieselben_textilien(self):
        """Beide Kategorien haben dasselbe Sortiment - nur andere Größen."""
        def grundtitel(kategorie):
            """Die Titel einer Kategorie ohne das angehaengte ', Damen'/', Herren'."""
            artikel = self.anwendung.artikel_service.suchen(kategorie=kategorie)
            return {a.titel.removesuffix(f", {kategorie}") for a in artikel}

        self.assertEqual(grundtitel("Damen"), grundtitel("Herren"))
        self.assertGreaterEqual(len(grundtitel("Damen")), 6)

    def test_fleecejacke_gibt_es_je_kategorie_einmal(self):
        """Sie war früher zweimal drin - und nur bei Herren."""
        treffer = self.anwendung.artikel_service.suchen(suchtext="Fleecejacke")
        kategorien = sorted(a.kategorie for a in treffer)

        self.assertEqual(kategorien, ["Damen", "Herren"])

    def test_kleidung_hat_die_groessen_ihrer_kategorie(self):
        """Kleidung hat die Größen ihrer Kategorie."""
        for artikel in self.anwendung.artikel_service.alle():
            self.assertEqual(
                artikel.groessen,
                konfiguration.groessen_fuer(artikel.kategorie),
                f"Falsche Größen bei {artikel.titel}",
            )

    def test_beispielbestellungen_haben_bei_kleidung_eine_groesse(self):
        """Beispielbestellungen haben bei Kleidung eine Größe."""
        zeilen = self.anwendung.datenbank.abfragen(
            """SELECT a.kategorie, p.groesse
               FROM bestellposition p
               JOIN artikel a ON a.artikel_id = p.artikel_id"""
        )
        for zeile in zeilen:
            erwartet = konfiguration.groessen_fuer(zeile["kategorie"])
            if erwartet:
                self.assertIn(zeile["groesse"], erwartet)
            else:
                self.assertIsNone(zeile["groesse"])


if __name__ == "__main__":
    unittest.main()
