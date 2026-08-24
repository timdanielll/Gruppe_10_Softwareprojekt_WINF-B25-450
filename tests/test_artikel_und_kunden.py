"""Tests für Artikelverwaltung und Kundenkartei (/F21/–/F23/, /F41/–/F44/)."""

import unittest

from fanshop import konfiguration
from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle.artikel import Artikel, Kleidungsartikel
from tests.basis import FanshopTest


class ArtikelTest(FanshopTest):

    # -- /F21/ Anlegen und Vererbung ---------------------------------------

    def test_kleidung_wird_zu_kleidungsartikel(self):
        """Damen und Herren erzeugen die Unterklasse mit Größenspanne (/NF20/)."""
        artikel = self.artikel_anlegen("Hoodie", "Herren")
        geladen = self.artikel_service.laden(artikel.artikel_id)

        self.assertIsInstance(geladen, Kleidungsartikel)
        self.assertTrue(geladen.braucht_groesse)
        self.assertIn("Größen", geladen.merkmale())

    def test_andere_kategorien_bleiben_normale_artikel(self):
        """Andere Kategorien bleiben normale Artikel."""
        artikel = self.artikel_anlegen("Tasse", "Accessoires")
        geladen = self.artikel_service.laden(artikel.artikel_id)

        self.assertIsInstance(geladen, Artikel)
        self.assertNotIsInstance(geladen, Kleidungsartikel)
        self.assertEqual(geladen.merkmale(), "")

    def test_endpreis_zieht_den_artikelrabatt_ab(self):
        """Endpreis zieht den artikelrabatt ab."""
        artikel = self.artikel_anlegen("Schirm", "Accessoires", preis=20.00, rabattsatz=0.15)
        self.assertAlmostEqual(artikel.endpreis, 17.00)

    # -- Pruefungen (/NF11/) -----------------------------------------------

    def test_leerer_titel_wird_abgelehnt(self):
        """Leerer Titel wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_anlegen(titel="   ")

    def test_preis_null_wird_abgelehnt(self):
        """Preis Null wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_anlegen(preis=0.0)

    def test_unbekannte_kategorie_wird_abgelehnt(self):
        """Unbekannte Kategorie wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_anlegen(kategorie="Möbel")

    def test_negativer_lagerbestand_wird_abgelehnt(self):
        """Negativer Lagerbestand wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_anlegen(lagerbestand=-1)

    def test_rabattsatz_ueber_100_prozent_wird_abgelehnt(self):
        """Rabattsatz über 100 Prozent wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_anlegen(rabattsatz=1.5)

    # -- /F22/ Soft-Delete -------------------------------------------------

    def test_deaktivierter_artikel_bleibt_in_der_datenbank(self):
        """Deaktivierter Artikel bleibt in der Datenbank."""
        artikel = self.artikel_anlegen()
        self.artikel_service.deaktivieren(artikel.artikel_id)

        self.assertEqual(len(self.artikel_service.alle(nur_aktive=True)), 0)
        self.assertEqual(len(self.artikel_service.alle(nur_aktive=False)), 1)
        self.assertFalse(self.artikel_service.laden(artikel.artikel_id).aktiv)

    # -- /F23/ Suche -------------------------------------------------------

    def test_suche_kombiniert_alle_filter(self):
        """Suche kombiniert alle Filter."""
        self.artikel_anlegen("Tasse htw saar", "Accessoires", preis=9.90)
        self.artikel_anlegen("Hoodie htw saar", "Herren", preis=44.90)
        self.artikel_anlegen("Kugelschreiber", "Schreibwaren", preis=2.50)

        # /F233/ Volltext
        self.assertEqual(len(self.artikel_service.suchen(suchtext="htw")), 2)
        # /F231/ Kategorie
        self.assertEqual(len(self.artikel_service.suchen(kategorie="Herren")), 1)
        # /F232/ Preisspanne
        self.assertEqual(len(self.artikel_service.suchen(min_preis=5.0, max_preis=20.0)), 1)
        # Kombination
        treffer = self.artikel_service.suchen(suchtext="htw", max_preis=20.0)
        self.assertEqual(len(treffer), 1)
        self.assertEqual(treffer[0].titel, "Tasse htw saar")

    def test_suche_findet_auch_in_der_beschreibung(self):
        """Suche findet auch in der beschreibung."""
        self.artikel_service.anlegen(
            titel="Lineal",
            kategorie="Schreibwaren",
            preis=1.50,
            lagerbestand=10,
            beschreibung="Aus recyceltem Kunststoff",
        )
        self.assertEqual(len(self.artikel_service.suchen(suchtext="recycelt")), 1)

    def test_umgekehrte_preisspanne_wird_abgelehnt(self):
        """Umgekehrte Preisspanne wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.artikel_service.suchen(min_preis=50.0, max_preis=10.0)


class KundenTest(FanshopTest):

    # -- /F42/ Anlegen -----------------------------------------------------

    def test_kunde_bekommt_eine_nummer(self):
        """Kunde bekommt eine nummer."""
        kunde = self.kunde_anlegen()
        self.assertIsNotNone(kunde.kundennummer)

    def test_pflichtfelder_werden_geprueft(self):
        """Pflichtfelder werden geprüft."""
        with self.assertRaises(ValidierungsFehler):
            self.kunden_service.anlegen(name="", strasse="Weg 1", plz=66117, ort="SB")
        with self.assertRaises(ValidierungsFehler):
            self.kunden_service.anlegen(name="A", strasse="Weg 1", plz=123, ort="SB")

    def test_postleitzahl_mit_fuehrender_null(self):
        """01067 Dresden muss gehen - die Null geht in INTEGER verloren."""
        kunde = self.kunden_service.anlegen(
            name="Dora Klein", strasse="Altmarkt 1", plz=1067, ort="Dresden"
        )
        geladen = self.kunden_service.laden(kunde.kundennummer)
        self.assertEqual(geladen.plz, 1067)
        self.assertEqual(geladen.plz_text, "01067")
        self.assertIn("01067", geladen.anschrift)

    def test_zu_kurze_postleitzahl_wird_abgelehnt(self):
        """Zu kurze Postleitzahl wird abgelehnt."""
        with self.assertRaises(ValidierungsFehler):
            self.kunden_service.anlegen(
                name="A", strasse="Weg 1", plz=99, ort="Nirgendwo"
            )

    def test_stickerstand_bleibt_beim_speichern_erhalten(self):
        """Ein Adressupdate darf den Sammelstand nicht zurücksetzen."""
        kunde = self.kunde_anlegen()
        artikel = self.artikel_anlegen()
        self.kassen_service.kunde_waehlen(kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(artikel.artikel_id, 1)
        self.kassen_service.kauf_abschliessen()

        veraltet = self.kunden_service.laden(kunde.kundennummer)
        veraltet.sticker_kontostand = 0          # veraltetes Objekt
        veraltet.ort = "Merzig"
        self.kunden_service.aktualisieren(veraltet)

        frisch = self.kunden_service.laden(kunde.kundennummer)
        self.assertEqual(frisch.ort, "Merzig")
        self.assertEqual(frisch.sticker_kontostand, konfiguration.STICKER_PRO_EINKAUF)

    def test_newsletter_anmeldung_schaltet_den_gutschein_frei(self):
        """Newsletter anmeldung schaltet den Gutschein frei."""
        kunde = self.kunde_anlegen(newsletter=True)
        self.assertTrue(kunde.darf_newsletter_rabatt_nutzen)

    def test_abmeldung_nimmt_den_gutschein_zurueck(self):
        """Abmeldung nimmt den Gutschein zurück."""
        kunde = self.kunde_anlegen(newsletter=True)
        aktualisiert = self.kunden_service.newsletter_umschalten(kunde.kundennummer, False)
        self.assertFalse(aktualisiert.newsletter_aktiv)
        self.assertFalse(aktualisiert.darf_newsletter_rabatt_nutzen)

    # -- /F44/ Suche -------------------------------------------------------

    def test_suche_nach_name_und_nummer(self):
        """Suche nach name und nummer."""
        kunde = self.kunde_anlegen("Anna Becker")
        self.kunde_anlegen("Ben Hoffmann")

        self.assertEqual(len(self.kunden_service.suchen("Becker")), 1)
        self.assertEqual(len(self.kunden_service.suchen(str(kunde.kundennummer))), 1)
        # Leerer Suchtext liefert alle
        self.assertEqual(len(self.kunden_service.suchen("")), 2)

    # -- /F43/ Loeschen mit Anonymisierung ---------------------------------

    def test_loeschen_anonymisiert_die_bestellungen(self):
        """Löschen anonymisiert die Bestellungen."""
        kunde = self.kunde_anlegen()
        artikel = self.artikel_anlegen()
        self.kassen_service.kunde_waehlen(kunde.kundennummer)
        self.kassen_service.artikel_hinzufuegen(artikel.artikel_id, 1)
        beleg = self.kassen_service.kauf_abschliessen()

        self.kunden_service.loeschen(kunde.kundennummer)

        with self.assertRaises(NichtGefundenFehler):
            self.kunden_service.laden(kunde.kundennummer)

        # Die Bestellung existiert weiter, ohne Kundenzuordnung.
        bestellung = self.anwendung.bestell_repository.laden(beleg.bestellnummer)
        self.assertIsNotNone(bestellung)
        self.assertIsNone(bestellung.kundennummer)
        self.assertEqual(bestellung.kunde_anzeige, "Geloeschter Kunde")

    def test_unbekannten_kunden_loeschen(self):
        """Unbekannten Kunden Löschen."""
        with self.assertRaises(NichtGefundenFehler):
            self.kunden_service.loeschen(9999)


if __name__ == "__main__":
    unittest.main()
