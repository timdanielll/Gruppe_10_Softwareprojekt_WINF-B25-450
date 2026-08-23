"""Der Zusammenbau der Anwendung.

Diese Klasse ist die Stelle, an der die Schichten zusammengesteckt werden:
Datenbank -> Repositories -> Services. Danach reicht ein einziges Objekt
durch die ganze GUI.

Warum das gut ist: Kein GUI-Fenster erzeugt selbst eine Datenbankverbindung.
Fuer einen Test genuegt::

    anwendung = Anwendung(datenbank_pfad=":memory:", testdaten=False)

und die komplette Logik laeuft ohne Oberflaeche (/NF21/).
"""

from pathlib import Path

from fanshop.datenbank.testdaten import testdaten_anlegen
from fanshop.datenbank.verbindung import Datenbank, datenbank_vorbereiten
from fanshop.logik.artikel_service import ArtikelService
from fanshop.logik.bericht_service import BerichtService
from fanshop.logik.kassen_service import KassenService
from fanshop.logik.kunden_service import KundenService
from fanshop.logik.retouren_service import RetourenService
from fanshop.logik.sonderaktion_service import SonderaktionService
from fanshop.repositories.artikel_repository import ArtikelRepository
from fanshop.repositories.bericht_repository import BerichtRepository
from fanshop.repositories.bestell_repository import BestellRepository
from fanshop.repositories.kunden_repository import KundenRepository
from fanshop.repositories.sonderaktion_repository import SonderaktionRepository


class Anwendung:
    """Haelt Datenbank, Repositories und Services zusammen."""

    def __init__(
        self,
        datenbank_pfad: Path | str | None = None,
        testdaten: bool = True,
    ) -> None:
        # 1. Datenbank oeffnen und Tabellen sicherstellen
        self.datenbank: Datenbank = datenbank_vorbereiten(datenbank_pfad)

        # 2. Repositories (Datenzugriff)
        self.artikel_repository = ArtikelRepository(self.datenbank)
        self.kunden_repository = KundenRepository(self.datenbank)
        self.bestell_repository = BestellRepository(self.datenbank)
        self.bericht_repository = BerichtRepository(self.datenbank)
        self.sonderaktion_repository = SonderaktionRepository(self.datenbank)

        # 3. Services (Geschaeftslogik)
        self.artikel_service = ArtikelService(self.artikel_repository)
        self.kunden_service = KundenService(self.kunden_repository)
        self.kassen_service = KassenService(
            self.artikel_repository,
            self.kunden_repository,
            self.bestell_repository,
            self.sonderaktion_repository,
        )
        self.retouren_service = RetourenService(self.bestell_repository)
        self.sonderaktion_service = SonderaktionService(self.sonderaktion_repository)
        self.bericht_service = BerichtService(self.bericht_repository)

        # 4. Beim allerersten Start: Beispieldaten (Pflichtenheft 8.2)
        self.testdaten_wurden_angelegt = False
        if testdaten:
            self.testdaten_wurden_angelegt = testdaten_anlegen(self.datenbank)

    def schliessen(self) -> None:
        """Schliesst die Datenbankverbindung beim Beenden des Programms."""
        self.datenbank.schliessen()

    def __repr__(self) -> str:
        return f"<Anwendung datenbank={self.datenbank.pfad}>"
