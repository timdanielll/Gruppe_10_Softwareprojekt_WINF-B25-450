"""Retourenabwicklung im Ladenlokal (/F51/).

Ablauf am Tresen: Der Kunde kommt mit seinem Beleg vorbei, der Bediener sucht
die Bestellnummer, waehlt die Position aus und gibt die Menge an. Das System
bucht die Ware zurueck ins Lager und rechnet die Erstattung aus.
"""

from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle.bestellung import Bestellung
from fanshop.modelle.retoure import Retoure
from fanshop.repositories.bestell_repository import BestellRepository


class RetourenService:
    """Nimmt Waren zurueck und erstattet Geld."""

    def __init__(self, bestell_repository: BestellRepository) -> None:
        self.bestell_repository = bestell_repository

    # -- Suchen ------------------------------------------------------------

    def bestellung_suchen(self, bestellnummer: int) -> Bestellung:
        """Laedt die Bestellung zum Beleg des Kunden.

        :raises NichtGefundenFehler: wenn es die Bestellnummer nicht gibt
        """
        bestellung = self.bestell_repository.laden(bestellnummer)
        if bestellung is None:
            raise NichtGefundenFehler(
                f"Es gibt keine Bestellung mit der Nummer {bestellnummer}."
            )
        return bestellung

    def letzte_bestellungen(self, anzahl: int = 50) -> list[Bestellung]:
        """Die neuesten Bestellungen - als Hilfe, wenn der Kunde den Beleg vergessen hat."""
        return self.bestell_repository.letzte(anzahl)

    def offene_menge(self, bestellnummer: int, artikel_id: int, gekaufte_menge: int) -> int:
        """Wie viele Stueck dieser Position koennen noch zurueckgegeben werden?"""
        return gekaufte_menge - self.bestell_repository.bereits_retourniert(
            bestellnummer, artikel_id
        )

    # -- /F51/ Retoure buchen ----------------------------------------------

    def retoure_buchen(self, bestellnummer: int, artikel_id: int, menge: int) -> Retoure:
        """Bucht eine Rueckgabe und gibt den Retourenbeleg zurueck (/F51/).

        Geprueft wird dreierlei:

        1. Gibt es die Bestellung ueberhaupt?
        2. War der Artikel in dieser Bestellung enthalten?
        3. Ist die Menge plausibel - also groesser als 0 und nicht mehr, als
           nach bereits erfolgten Teilretouren noch offen ist?

        Erstattet wird zum ``historischen_preis`` der Position, also zu dem
        Betrag, den der Kunde tatsaechlich gezahlt hat. Ein zwischenzeitlich
        geaenderter Verkaufspreis spielt keine Rolle.
        """
        if menge < 1:
            raise ValidierungsFehler("Die Retourenmenge muss mindestens 1 betragen.")

        bestellung = self.bestellung_suchen(bestellnummer)

        position = None
        for kandidat in bestellung.positionen:
            if kandidat.artikel_id == artikel_id:
                position = kandidat
                break

        if position is None:
            raise ValidierungsFehler(
                f"Dieser Artikel war nicht Teil der Bestellung {bestellnummer}."
            )

        noch_offen = self.offene_menge(bestellnummer, artikel_id, position.menge)
        if noch_offen <= 0:
            raise ValidierungsFehler(
                f"„{position.artikel_titel}“ wurde aus dieser Bestellung bereits "
                "vollständig zurückgegeben."
            )
        if menge > noch_offen:
            raise ValidierungsFehler(
                f"Es können nur noch {noch_offen} Stück von "
                f"„{position.artikel_titel}“ zurückgegeben werden."
            )

        retoure = self.bestell_repository.retoure_verbuchen(
            bestellnummer=bestellnummer,
            artikel_id=artikel_id,
            menge=menge,
            historischer_preis=position.historischer_preis,
        )
        # Titel nachtragen, damit die GUI den Beleg ohne weitere Abfrage anzeigen kann.
        retoure.artikel_titel = position.artikel_titel
        return retoure

    def retouren_zu(self, bestellnummer: int) -> list[Retoure]:
        """Bisherige Retouren einer Bestellung - fuer die Anzeige im Terminal."""
        return self.bestell_repository.retouren_zu(bestellnummer)
