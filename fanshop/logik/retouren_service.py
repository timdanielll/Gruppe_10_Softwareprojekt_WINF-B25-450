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
        """Merkt sich das Bestell-Repository."""
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

    def offene_menge(self, position_id: int, gekaufte_menge: int) -> int:
        """Wie viele Stueck dieser Bestellzeile koennen noch zurueck?"""
        return gekaufte_menge - self.bestell_repository.bereits_retourniert(position_id)

    # -- /F51/ Retoure buchen ----------------------------------------------

    def retoure_buchen(self, bestellnummer: int, position_id: int, menge: int) -> Retoure:
        """Bucht eine Rueckgabe und gibt den Retourenbeleg zurueck (/F51/).

        Zurueckgegeben wird eine **Bestellzeile**, nicht ein Artikel: Seit die
        Groesse beim Bestellen gewaehlt wird, kann derselbe Artikel zweimal in
        einer Bestellung stehen (etwa ein Hoodie in M und einer in L). Nur die
        Positionsnummer sagt eindeutig, welche der beiden gemeint ist.

        Geprueft wird dreierlei:

        1. Gibt es die Bestellung ueberhaupt?
        2. Gehoert die Position zu dieser Bestellung?
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
            if kandidat.position_id == position_id:
                position = kandidat
                break

        if position is None:
            raise ValidierungsFehler(
                f"Diese Position gehört nicht zur Bestellung {bestellnummer}."
            )

        noch_offen = self.offene_menge(position_id, position.menge)
        if noch_offen <= 0:
            raise ValidierungsFehler(
                f"„{position.anzeigename}“ wurde aus dieser Bestellung bereits "
                "vollständig zurückgegeben."
            )
        if menge > noch_offen:
            raise ValidierungsFehler(
                f"Es können nur noch {noch_offen} Stück von "
                f"„{position.anzeigename}“ zurückgegeben werden."
            )

        retoure = self.bestell_repository.retoure_verbuchen(
            bestellnummer=bestellnummer,
            position_id=position_id,
            artikel_id=position.artikel_id,
            menge=menge,
            historischer_preis=position.historischer_preis,
        )
        # Titel und Groesse nachtragen, damit die GUI den Beleg ohne weitere
        # Abfrage anzeigen kann.
        retoure.artikel_titel = position.artikel_titel
        retoure.groesse = position.groesse
        return retoure

    def retouren_zu(self, bestellnummer: int) -> list[Retoure]:
        """Bisherige Retouren einer Bestellung - fuer die Anzeige im Terminal."""
        return self.bestell_repository.retouren_zu(bestellnummer)
