"""Gemeinsame Grundlage aller Tests.

``FanshopTest`` legt für jeden einzelnen Testfall eine frische, leere Datenbank
im Arbeitsspeicher an. Dadurch können sich die Tests nicht gegenseitig
beeinflussen, und die echte ``fanshop.db`` wird nie angefasst.
"""

import unittest

from fanshop.logik.anwendung import Anwendung


class FanshopTest(unittest.TestCase):
    """Basisklasse: frische Datenbank je Testfall, plus kleine Hilfsmethoden."""

    def setUp(self) -> None:
        # ":memory:" = Datenbank nur im Arbeitsspeicher, verschwindet danach.
        # testdaten=False, damit jeder Test genau die Daten hat, die er anlegt.
        self.anwendung = Anwendung(datenbank_pfad=":memory:", testdaten=False)

        self.artikel_service = self.anwendung.artikel_service
        self.kunden_service = self.anwendung.kunden_service
        self.kassen_service = self.anwendung.kassen_service
        self.retouren_service = self.anwendung.retouren_service
        self.bericht_service = self.anwendung.bericht_service

    def tearDown(self) -> None:
        self.anwendung.schliessen()

    # -- Hilfen zum Anlegen von Testdaten ----------------------------------

    def artikel_anlegen(
        self,
        titel: str = "Tasse htw saar",
        kategorie: str = "Accessoires",
        preis: float = 10.00,
        lagerbestand: int = 10,
        rabattsatz: float = 0.0,
        groesse: str = "",
    ):
        return self.artikel_service.anlegen(
            titel=titel,
            kategorie=kategorie,
            preis=preis,
            lagerbestand=lagerbestand,
            rabattsatz=rabattsatz,
            groesse=groesse,
        )

    def kunde_anlegen(self, name: str = "Anna Becker", newsletter: bool = False):
        return self.kunden_service.anlegen(
            name=name,
            strasse="Waldhausweg 14",
            plz=66123,
            ort="Saarbrücken",
            newsletter=newsletter,
        )

    def sonderaktion_anlegen(
        self,
        titel: str = "Testaktion",
        art: str = "kategorie",
        rabattsatz: float = 0.20,
        zielkategorie: str | None = "Schreibwaren",
        mindestbestellwert: float = 0.0,
        aktiv: bool = True,
    ):
        from fanshop.modelle.sonderaktion import Sonderaktion

        aktion = Sonderaktion(
            titel=titel,
            art=art,
            rabattsatz=rabattsatz,
            zielkategorie=zielkategorie,
            mindestbestellwert=mindestbestellwert,
            aktiv=aktiv,
        )
        self.anwendung.sonderaktion_repository.speichern(aktion)
        return aktion
