"""Geschaeftslogik rund um Kunden (/F41/ bis /F44/, /F52/, /F53/)."""

from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle import starterset as starterset_modell
from fanshop.modelle import sticker as sticker_modell
from fanshop.modelle.kunde import Kunde
from fanshop.repositories.bestell_repository import BestellRepository
from fanshop.repositories.kunden_repository import KundenRepository


class StartersetStand:
    """Der Starterset-Stand eines Kunden - alles, was die Kartei dazu zeigt (/F53/)."""

    def __init__(
        self,
        erhalten: bool,
        anzahl_bestellungen: int,
        sammlung_vollstaendig: bool,
    ) -> None:
        self.erhalten = erhalten
        self.anzahl_bestellungen = anzahl_bestellungen
        self.sammlung_vollstaendig = sammlung_vollstaendig

    @property
    def fehlende_bestellungen(self) -> int:
        """Wie viele Einkaeufe noch fehlen (0 = Bedingung erfuellt)."""
        return starterset_modell.fehlende_bestellungen(self.anzahl_bestellungen)

    @property
    def anspruch_offen(self) -> bool:
        """True, wenn alle Bedingungen erfuellt sind, das Set aber noch aussteht.

        Das kann nur zwischen zwei Kaeufen auftreten - normalerweise wird das
        Set im selben Moment gebucht, in dem die Sammlung voll wird.
        """
        return (
            not self.erhalten
            and self.sammlung_vollstaendig
            and self.fehlende_bestellungen == 0
        )

    def __str__(self) -> str:
        if self.erhalten:
            return f"{starterset_modell.TITEL} erhalten"
        return f"{starterset_modell.TITEL} offen"


class KundenService:
    """Alles, was mit der Kundenkartei passiert."""

    def __init__(
        self,
        kunden_repository: KundenRepository,
        bestell_repository: BestellRepository | None = None,
    ) -> None:
        self.kunden_repository = kunden_repository
        # Nur fuer den Starterset-Stand noetig: Der haengt an der Zahl der
        # abgeschlossenen Einkaeufe, und die weiss allein das Bestell-Repository.
        self.bestell_repository = bestell_repository

    # -- Pruefungen --------------------------------------------------------

    @staticmethod
    def pruefen(name: str, strasse: str, plz: int, ort: str) -> None:
        """Prueft die Pflichtfelder der Kundenmaske (/F42/)."""
        if not name.strip():
            raise ValidierungsFehler("Bitte den Namen des Kunden eingeben.")
        if not strasse.strip():
            raise ValidierungsFehler("Bitte Straße und Hausnummer eingeben.")
        if not ort.strip():
            raise ValidierungsFehler("Bitte den Wohnort eingeben.")
        # Deutsche Postleitzahlen laufen von 01067 bis 99998. Weil die Spalte
        # laut Pflichtenheft INTEGER ist, geht die fuehrende Null beim Speichern
        # verloren - 01067 wird zu 1067. Die Anzeige stellt sie ueber
        # kunde.plz_text wieder her.
        if not 1000 <= plz <= 99999:
            raise ValidierungsFehler(
                "Die Postleitzahl muss fünfstellig sein (z. B. 66117 oder 01067)."
            )

    # -- /F42/ Anlegen -----------------------------------------------------

    def anlegen(
        self,
        name: str,
        strasse: str,
        plz: int,
        ort: str,
        newsletter: bool = False,
    ) -> Kunde:
        """Legt einen Kunden an; die Kundennummer vergibt die Datenbank (/F42/).

        Meldet sich der Kunde gleich zum Newsletter an, bekommt er den
        einmaligen 10-Prozent-Gutschein sofort gutgeschrieben (/F52/).
        """
        self.pruefen(name, strasse, plz, ort)

        kunde = Kunde(
            name=name.strip(),
            strasse=strasse.strip(),
            plz=plz,
            ort=ort.strip(),
            newsletter_aktiv=newsletter,
            newsletter_rabatt_verfuegbar=newsletter,
        )
        self.kunden_repository.speichern(kunde)
        return kunde

    def aktualisieren(self, kunde: Kunde) -> None:
        self.pruefen(kunde.name, kunde.strasse, kunde.plz, kunde.ort)
        self.kunden_repository.aktualisieren(kunde)

    # -- /F41/, /F44/ Lesen und Suchen -------------------------------------

    def alle(self) -> list[Kunde]:
        """Alle Kunden (/F41/)."""
        return self.kunden_repository.alle()

    def suchen(self, suchtext: str) -> list[Kunde]:
        """Sucht nach Name oder Kundennummer (/F44/).

        Ein leerer Suchtext liefert alle Kunden - so muss die GUI keinen
        Sonderfall behandeln.
        """
        if not suchtext.strip():
            return self.alle()
        return self.kunden_repository.suchen(suchtext)

    def laden(self, kundennummer: int) -> Kunde:
        kunde = self.kunden_repository.laden(kundennummer)
        if kunde is None:
            raise NichtGefundenFehler(f"Es gibt keinen Kunden mit der Nummer {kundennummer}.")
        return kunde

    # -- /F43/ Loeschen ----------------------------------------------------

    def loeschen(self, kundennummer: int) -> None:
        """Loescht einen Kunden und anonymisiert seine Bestellungen (/F43/)."""
        if not self.kunden_repository.existiert(kundennummer):
            raise NichtGefundenFehler(f"Es gibt keinen Kunden mit der Nummer {kundennummer}.")
        self.kunden_repository.loeschen_und_anonymisieren(kundennummer)

    # -- /F53/ Sticker-Sammelalbum -----------------------------------------

    def sticker_album(self, kundennummer: int) -> dict[str, int]:
        """Welche Stickermotive besitzt der Kunde (/F53/)?

        Jedes Motiv gibt es nur einmal, die Anzahl ist also immer 1.
        """
        return self.kunden_repository.sticker_album(kundennummer)

    def starterset_stand(self, kundennummer: int) -> StartersetStand:
        """Der Stand des Starterset-Sonderangebots fuer diesen Kunden (/F53/).

        Ohne Bestell-Repository (etwa in einem sehr schlanken Testaufbau) bleibt
        die Zahl der Einkaeufe 0 - der Stand zeigt dann nur, ob das Set schon
        vergeben wurde.
        """
        album = self.kunden_repository.sticker_album(kundennummer)
        anzahl = (
            self.bestell_repository.anzahl_bestellungen(kundennummer)
            if self.bestell_repository is not None
            else 0
        )
        return StartersetStand(
            erhalten=self.kunden_repository.starterset_erhalten(kundennummer),
            anzahl_bestellungen=anzahl,
            sammlung_vollstaendig=sticker_modell.album_vollstaendig(album),
        )

    # -- /F52/ Newsletter --------------------------------------------------

    def newsletter_umschalten(self, kundennummer: int, angemeldet: bool) -> Kunde:
        """Meldet einen Kunden zum Newsletter an oder ab (/F52/).

        :return: den frisch geladenen Kunden, damit die GUI den neuen Zustand
                 (Gutschein ja/nein) direkt anzeigen kann.
        """
        self.kunden_repository.newsletter_setzen(kundennummer, angemeldet)
        return self.laden(kundennummer)
