"""Geschaeftslogik rund um Artikel (/F21/ bis /F25/).

Die Services sind die Schicht zwischen GUI und Repositories. Sie pruefen
Eingaben, bevor etwas in die Datenbank geschrieben wird, und sie sind der
einzige Gespraechspartner der Oberflaeche. Die GUI kennt kein Repository.
"""

from fanshop import konfiguration
from fanshop.fehler import NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle.artikel import Artikel, Kleidungsartikel
from fanshop.repositories.artikel_repository import ArtikelRepository

#: Beschriftung fuer "dieser Artikel hat kein Foto".
OHNE_FOTO = "– kein Foto –"


class ArtikelService:
    """Alles, was mit dem Sortiment passiert."""

    def __init__(self, artikel_repository: ArtikelRepository) -> None:
        self.artikel_repository = artikel_repository

    # -- Pruefungen --------------------------------------------------------

    @staticmethod
    def pruefen(
        titel: str,
        kategorie: str,
        preis: float,
        lagerbestand: int,
        rabattsatz: float,
        groesse: str = "",
    ) -> None:
        """Prueft die Eingaben einer Artikelmaske (/NF11/).

        Wirft beim ersten Problem einen ``ValidierungsFehler`` mit einem Text,
        den die GUI unveraendert im Dialogfenster anzeigen kann.
        """
        if not titel.strip():
            raise ValidierungsFehler("Bitte einen Titel für den Artikel eingeben.")

        if kategorie not in konfiguration.KATEGORIEN:
            raise ValidierungsFehler(
                "Bitte eine der vorgegebenen Kategorien auswählen: "
                + ", ".join(konfiguration.KATEGORIEN)
            )

        if preis <= 0:
            raise ValidierungsFehler("Der Preis muss größer als 0,00 € sein.")

        if lagerbestand < 0:
            raise ValidierungsFehler("Der Lagerbestand kann nicht negativ sein.")

        if not 0.0 <= rabattsatz < 1.0:
            raise ValidierungsFehler(
                "Der Rabattsatz muss zwischen 0 % und 99 % liegen "
                "(Eingabe als Dezimalzahl, z. B. 0,15 für 15 %)."
            )

        if kategorie in konfiguration.KLEIDUNGS_KATEGORIEN and groesse:
            if groesse not in konfiguration.GROESSEN:
                raise ValidierungsFehler(
                    "Ungültige Größe. Erlaubt sind: " + ", ".join(konfiguration.GROESSEN)
                )

    # -- /F21/ Artikel anlegen ---------------------------------------------

    def anlegen(
        self,
        titel: str,
        kategorie: str,
        preis: float,
        lagerbestand: int,
        beschreibung: str = "",
        rabattsatz: float = 0.0,
        groesse: str = "",
        bildpfad: str | None = None,
    ) -> Artikel:
        """Legt einen neuen Artikel an (/F21/).

        Welche Klasse entsteht, entscheidet die Kategorie: Damen und Herren
        werden zu ``Kleidungsartikel`` (mit Groesse), alles andere zu ``Artikel``.
        """
        self.pruefen(titel, kategorie, preis, lagerbestand, rabattsatz, groesse)

        gemeinsam = dict(
            titel=titel.strip(),
            kategorie=kategorie,
            preis=preis,
            lagerbestand=lagerbestand,
            beschreibung=beschreibung.strip(),
            rabattsatz=rabattsatz,
            bildpfad=bildpfad,
        )
        if kategorie in konfiguration.KLEIDUNGS_KATEGORIEN:
            artikel = Kleidungsartikel(groesse=groesse, **gemeinsam)
        else:
            artikel = Artikel(**gemeinsam)

        self.artikel_repository.speichern(artikel)
        return artikel

    # -- /F22/ Artikel pflegen ---------------------------------------------

    def aktualisieren(self, artikel: Artikel) -> None:
        """Speichert Aenderungen an einem vorhandenen Artikel (/F22/)."""
        self.pruefen(
            artikel.titel,
            artikel.kategorie,
            artikel.preis,
            artikel.lagerbestand,
            artikel.rabattsatz,
            getattr(artikel, "groesse", ""),
        )
        self.artikel_repository.aktualisieren(artikel)

    def bestand_setzen(self, artikel_id: int, neuer_bestand: int) -> None:
        """Aendert den Lagerbestand (/F22/, Inline-Bearbeitung in der Tabelle)."""
        if neuer_bestand < 0:
            raise ValidierungsFehler("Der Lagerbestand kann nicht negativ sein.")
        if not self.artikel_repository.existiert(artikel_id):
            raise NichtGefundenFehler(f"Es gibt keinen Artikel mit der Nummer {artikel_id}.")
        self.artikel_repository.bestand_setzen(artikel_id, neuer_bestand)

    def deaktivieren(self, artikel_id: int) -> None:
        """Nimmt einen Artikel aus dem Verkauf (Soft-Delete, /F22/).

        Es wird bewusst nicht geloescht: alte Bestellungen und Retouren
        verweisen auf diesen Artikel und muessen lesbar bleiben.
        """
        if not self.artikel_repository.existiert(artikel_id):
            raise NichtGefundenFehler(f"Es gibt keinen Artikel mit der Nummer {artikel_id}.")
        self.artikel_repository.deaktivieren(artikel_id)

    def aktivieren(self, artikel_id: int) -> None:
        """Stellt einen deaktivierten Artikel wieder in den Verkauf."""
        self.artikel_repository.aktivieren(artikel_id)

    # -- /F23/ Suchen ------------------------------------------------------

    def suchen(
        self,
        suchtext: str = "",
        kategorie: str = "",
        min_preis: float | None = None,
        max_preis: float | None = None,
        nur_aktive: bool = True,
    ) -> list[Artikel]:
        """Kombinierte Artikelsuche (/F231/ bis /F233/)."""
        if min_preis is not None and max_preis is not None and min_preis > max_preis:
            raise ValidierungsFehler(
                "Der Mindestpreis darf nicht größer als der Höchstpreis sein."
            )
        return self.artikel_repository.suchen(
            suchtext=suchtext,
            kategorie=kategorie,
            min_preis=min_preis,
            max_preis=max_preis,
            nur_aktive=nur_aktive,
        )

    def laden(self, artikel_id: int) -> Artikel:
        artikel = self.artikel_repository.laden(artikel_id)
        if artikel is None:
            raise NichtGefundenFehler(f"Es gibt keinen Artikel mit der Nummer {artikel_id}.")
        return artikel

    def alle(self, nur_aktive: bool = True) -> list[Artikel]:
        return self.artikel_repository.alle(nur_aktive=nur_aktive)

    # -- Produktfotos ------------------------------------------------------

    def bildauswahl(self) -> list[tuple[str, str | None]]:
        """Alle Produktfotos aus ``assets/artikel/`` als Auswahlliste.

        Ein neu angelegter Artikel hat zunaechst kein Foto. Damit man ihm eines
        geben kann, ohne Dateien zu kopieren, bietet die Maske die vorhandenen
        Bilder zur Auswahl an. Beschriftet werden sie mit dem Titel des
        Artikels, der das Bild schon benutzt - ein Dateiname wie
        "WhatsApp Image 2026-08-20 ..." sagt niemandem etwas.

        :return: Liste aus (Beschriftung, Dateiname); der erste Eintrag ist
                 immer "kein Foto" mit ``None`` als Dateiname
        """
        # Wer benutzt welches Bild? Daraus entstehen die Beschriftungen.
        benutzt: dict[str, str] = {}
        for artikel in self.artikel_repository.alle(nur_aktive=False):
            if artikel.bildpfad and artikel.bildpfad not in benutzt:
                benutzt[artikel.bildpfad] = artikel.titel

        verzeichnis = konfiguration.ARTIKELBILDER_VERZEICHNIS
        dateien = sorted(p.name for p in verzeichnis.glob("*.jpeg")) if verzeichnis.exists() else []

        auswahl: list[tuple[str, str | None]] = [(OHNE_FOTO, None)]
        for nummer, datei in enumerate(dateien, start=1):
            auswahl.append((benutzt.get(datei, f"Foto {nummer}"), datei))
        return auswahl

    # -- /F24/ und /F25/ ---------------------------------------------------

    def umsatzstaerkste(self, anzahl: int = 10) -> list[dict]:
        """Artikel mit dem hoechsten Umsatz (/F24/)."""
        return self.artikel_repository.umsatzstaerkste(anzahl)

    def haeufigste(self, anzahl: int = 10) -> list[dict]:
        """Am haeufigsten verkaufte Artikel (/F25/)."""
        return self.artikel_repository.haeufigste(anzahl)
