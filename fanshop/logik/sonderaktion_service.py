"""Geschaeftslogik fuer Sonderaktionen.

Das Lastenheft verlangt: "Es gibt fest (von Ihnen) definierte Spezialangebote,
die **aktiviert werden koennen**". Dieser Service ist das "koennen": Er ist der
einzige Weg, ueber den die Oberflaeche eine Aktion scharf schaltet.

Es ist immer hoechstens **eine** Aktion aktiv. Das haelt die Rabattrechnung
nachvollziehbar - der Bediener kann dem Kunden in einem Satz erklaeren, warum
der Preis so ist, wie er ist.
"""

from fanshop.fehler import NichtGefundenFehler
from fanshop.modelle.sonderaktion import Sonderaktion
from fanshop.repositories.sonderaktion_repository import SonderaktionRepository


class SonderaktionService:
    """Listet, aktiviert und beendet die Spezialangebote."""

    def __init__(self, sonderaktion_repository: SonderaktionRepository) -> None:
        """Merkt sich das Sonderaktion-Repository."""
        self.sonderaktion_repository = sonderaktion_repository

    def alle(self) -> list[Sonderaktion]:
        """Alle hinterlegten Aktionen - aktive wie inaktive."""
        return self.sonderaktion_repository.alle()

    def aktive(self) -> Sonderaktion | None:
        """Die gerade laufende Aktion, oder None."""
        return self.sonderaktion_repository.aktive()

    def aktivieren(self, aktions_id: int) -> Sonderaktion:
        """Schaltet genau eine Aktion scharf und alle anderen ab.

        :raises NichtGefundenFehler: wenn es die Aktion nicht gibt
        """
        if not self.sonderaktion_repository.existiert(aktions_id):
            raise NichtGefundenFehler(
                f"Es gibt keine Sonderaktion mit der Nummer {aktions_id}."
            )
        self.sonderaktion_repository.aktivieren(aktions_id)

        aktion = self.aktive()
        if aktion is None:
            # Kann nur passieren, wenn jemand parallel in die Datenbank schreibt.
            raise NichtGefundenFehler("Die Aktion konnte nicht aktiviert werden.")
        return aktion

    def beenden(self) -> None:
        """Beendet jede laufende Aktion.

        Wirkt nur auf **kommende** Bestellungen - bereits gebuchte Belege
        bleiben unveraendert, weil ihr Rabatt im historischen Preis steckt.
        """
        self.sonderaktion_repository.alle_deaktivieren()
