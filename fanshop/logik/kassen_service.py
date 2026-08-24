"""Der Kassiervorgang - das Herzstueck der Anwendung (/F11/ bis /F14/, /F52/, /F53/).

Der ``KassenService`` haelt den Zustand *einer* Bedienung: welcher Kunde gerade
am Tresen steht, was in seinem Warenkorb liegt und ob sein Newsletter-Gutschein
eingesetzt werden soll. Das entspricht der Betriebsbedingung aus dem
Pflichtenheft (Kapitel 2.3): "Das Programm verarbeitet pro Sitzung genau einen
aktiven Kunden."

Der lineare Ablauf aus /NF12/ bildet sich eins zu eins in den Methoden ab:

    kunde_waehlen -> artikel_hinzufuegen -> preisuebersicht -> kauf_abschliessen
"""

from fanshop import konfiguration
from fanshop.fehler import BestandsFehler, NichtGefundenFehler, ValidierungsFehler
from fanshop.modelle.kunde import Kunde
from fanshop.modelle import starterset as starterset_modell
from fanshop.modelle import sticker as sticker_modell
from fanshop.modelle.sonderaktion import Sonderaktion
from fanshop.modelle.warenkorb import Preisuebersicht, Warenkorb
from fanshop.repositories.artikel_repository import ArtikelRepository
from fanshop.repositories.bestell_repository import BestellRepository
from fanshop.repositories.kunden_repository import KundenRepository
from fanshop.repositories.sonderaktion_repository import SonderaktionRepository


class Kaufbeleg:
    """Das Ergebnis eines abgeschlossenen Kaufs - alles, was die GUI danach zeigt."""

    def __init__(
        self,
        bestellnummer: int,
        uebersicht: Preisuebersicht,
        sticker: int,
        kundenname: str,
        motive: list | None = None,
        album_stand: tuple[int, int] | None = None,
        starterset: bool = False,
    ) -> None:
        """Sammelt alles, was die GUI nach dem Kauf anzeigt."""
        self.bestellnummer = bestellnummer
        self.uebersicht = uebersicht
        self.sticker = sticker
        self.kundenname = kundenname
        #: Die konkreten Stickermotive dieses Einkaufs (/F53/).
        self.motive = motive or []
        #: (verschiedene Motive, Gesamtzahl) nach diesem Einkauf.
        self.album_stand = album_stand
        #: True, wenn diesem Kauf das Starterset beiliegt (/F53/).
        self.starterset = starterset

    @property
    def starterset_inhalt(self) -> tuple[str, ...]:
        """Was im Starterset steckt - leer, wenn es keins gab."""
        return starterset_modell.INHALT if self.starterset else ()

    def __str__(self) -> str:
        """Bestellnummer und Endbetrag."""
        return f"Bestellung {self.bestellnummer} über {self.uebersicht.gesamtbetrag:.2f} EUR"


class KassenService:
    """Fuehrt genau einen Kassiervorgang."""

    def __init__(
        self,
        artikel_repository: ArtikelRepository,
        kunden_repository: KundenRepository,
        bestell_repository: BestellRepository,
        sonderaktion_repository: SonderaktionRepository,
    ) -> None:
        """Merkt sich die Repositories und startet mit leerem Korb."""
        self.artikel_repository = artikel_repository
        self.kunden_repository = kunden_repository
        self.bestell_repository = bestell_repository
        self.sonderaktion_repository = sonderaktion_repository

        # Zustand der laufenden Bedienung
        self.warenkorb = Warenkorb()
        self.aktiver_kunde: Kunde | None = None
        self.newsletter_rabatt_anwenden = False

    # -- Kunde -------------------------------------------------------------

    def kunde_waehlen(self, kundennummer: int) -> Kunde:
        """Setzt den Kunden, der gerade bedient wird.

        Der Warenkorb bleibt dabei erhalten - beim Kassieren stellt man oft
        erst die Ware zusammen und ordnet den Kunden danach zu.
        """
        kunde = self.kunden_repository.laden(kundennummer)
        if kunde is None:
            raise NichtGefundenFehler(f"Es gibt keinen Kunden mit der Nummer {kundennummer}.")

        self.aktiver_kunde = kunde
        # Ein neuer Kunde bringt seinen eigenen Gutscheinstatus mit.
        self.newsletter_rabatt_anwenden = False
        return kunde

    def kunde_abwaehlen(self) -> None:
        """Laufkundschaft: Verkauf ohne Kundenprofil (dann gibt es keine Sticker)."""
        self.aktiver_kunde = None
        self.newsletter_rabatt_anwenden = False

    def newsletter_rabatt_moeglich(self) -> bool:
        """True, wenn fuer den aktiven Kunden der 10-Prozent-Gutschein offen ist (/F52/)."""
        return self.aktiver_kunde is not None and self.aktiver_kunde.darf_newsletter_rabatt_nutzen

    def newsletter_rabatt_setzen(self, anwenden: bool) -> None:
        """Schaltet den Gutschein fuer diesen Kauf ein oder aus.

        Die GUI sperrt die Checkbox, wenn kein Gutschein offen ist - hier wird
        derselbe Fall noch einmal geprueft, damit die Logik auch ohne GUI stimmt.
        """
        if anwenden and not self.newsletter_rabatt_moeglich():
            raise ValidierungsFehler(
                "Für diesen Kunden ist kein Newsletter-Rabatt verfügbar."
            )
        self.newsletter_rabatt_anwenden = anwenden

    # -- /F11/ bis /F13/ Warenkorb -----------------------------------------

    def artikel_hinzufuegen(
        self, artikel_id: int, menge: int = 1, groesse: str = ""
    ) -> None:
        """Legt einen Artikel in den Warenkorb (/F11/).

        Der Artikel wird absichtlich frisch aus der Datenbank geladen: Der
        Lagerbestand kann sich seit dem Aufbau der Artikelliste geaendert
        haben (z. B. durch eine Retoure).

        :param groesse: bei Damen- und Herrentextilien Pflicht, sonst leer
                        lassen. Welche Groessen es gibt, sagt
                        ``artikel.groessen``.
        """
        artikel = self.artikel_repository.laden(artikel_id)
        if artikel is None:
            raise NichtGefundenFehler(f"Es gibt keinen Artikel mit der Nummer {artikel_id}.")
        if not artikel.aktiv:
            raise ValidierungsFehler(f"„{artikel.titel}“ wird nicht mehr verkauft.")

        self.warenkorb.hinzufuegen(artikel, menge, groesse)

    def position_entfernen(self, schluessel: str) -> None:
        """Entfernt eine Warenkorbzeile vollstaendig (/F12/)."""
        self.warenkorb.entfernen(schluessel)

    def menge_setzen(self, schluessel: str, menge: int) -> None:
        """Setzt die Menge einer Warenkorbzeile neu (/F12/)."""
        self.warenkorb.menge_setzen(schluessel, menge)

    def warenkorb_leeren(self) -> None:
        """Wirft alles aus dem Warenkorb."""
        self.warenkorb.leeren()

    def groessen_fuer(self, artikel_id: int) -> tuple[str, ...]:
        """Welche Groessen sind fuer diesen Artikel waehlbar? (leer = keine)"""
        artikel = self.artikel_repository.laden(artikel_id)
        return artikel.groessen if artikel else ()

    def aktive_sonderaktion(self) -> Sonderaktion | None:
        """Die gerade laufende Rabattaktion - oder None."""
        return self.sonderaktion_repository.aktive()

    def preisuebersicht(self) -> Preisuebersicht:
        """Berechnet den aktuellen Bestellwert (/F13/).

        Die Rechnung selbst steht im Warenkorb; dieser Service reicht nur die
        aktive Sonderaktion und den Gutscheinstatus hinein.
        """
        return self.warenkorb.berechne(
            sonderaktion=self.aktive_sonderaktion(),
            newsletter_rabatt_anwenden=self.newsletter_rabatt_anwenden,
        )

    # -- /F14/ Kauf abschliessen -------------------------------------------

    def kauf_abschliessen(self) -> Kaufbeleg:
        """Schliesst den Einkauf ab (/F14/).

        Ablauf:

        1. Warenkorb darf nicht leer sein
        2. Lagerbestand wird noch einmal frisch geprueft
        3. Bestellwert wird berechnet
        4. Alles wird in einer Transaktion gebucht (Bestellung, Positionen,
           Lagerabgang, Sticker, Starterset, Gutschein)
        5. Warenkorb wird geleert, damit der naechste Kunde drankommt

        :return: den Kaufbeleg mit Bestellnummer, Summen, Stickern und dem
                 Hinweis, ob das Starterset beiliegt
        """
        if self.warenkorb.ist_leer:
            raise ValidierungsFehler("Der Warenkorb ist leer - es gibt nichts zu buchen.")

        self._bestand_erneut_pruefen()

        uebersicht = self.preisuebersicht()
        motive, starterset = self._praemien_bestimmen()
        sticker = len(motive)

        bestellnummer = self.bestell_repository.kauf_verbuchen(
            kundennummer=self.aktiver_kunde.kundennummer if self.aktiver_kunde else None,
            positionen=self.warenkorb.positionen,
            gesamtbetrag=uebersicht.gesamtbetrag,
            newsletter_rabatt_angewendet=self.newsletter_rabatt_anwenden,
            sticker=sticker,
            sticker_motive=[motiv.schluessel for motiv in motive],
            starterset=starterset,
        )

        kundenname = self.aktiver_kunde.name if self.aktiver_kunde else "Laufkundschaft"

        # Nach dem Kauf ist der Gutschein verbraucht und der Korb leer.
        self.warenkorb.leeren()
        self.newsletter_rabatt_anwenden = False

        album_stand = None
        if self.aktiver_kunde is not None:
            kundennummer = self.aktiver_kunde.kundennummer
            self.aktiver_kunde = self.kunden_repository.laden(kundennummer)
            album_stand = sticker_modell.album_fortschritt(
                self.kunden_repository.sticker_album(kundennummer)
            )

        return Kaufbeleg(
            bestellnummer,
            uebersicht,
            sticker,
            kundenname,
            motive,
            album_stand,
            starterset,
        )

    def _praemien_bestimmen(self) -> tuple[list, bool]:
        """Welche Sticker und welches Sonderangebot bringt dieser Kauf? (/F53/)

        Laufkundschaft geht leer aus - ohne Kundenkonto gibt es niemanden, dem
        man etwas gutschreiben koennte.

        Fuer alle anderen entscheidet **das Album**, nicht der Zaehler: Es
        werden genau die Motive vergeben, die noch fehlen - hoechstens
        ``STICKER_PRO_EINKAUF`` Stueck. Wer schon alle sechs hat, bekommt
        keinen Sticker mehr.

        Das Starterset kommt oben drauf, sobald die Sammlung mit diesem Kauf
        vollstaendig ist und der Kunde die noetige Zahl an Einkaeufen erreicht
        hat - einmalig, siehe ``modelle/starterset.py``.

        :return: (Motive dieses Kaufs, True wenn das Starterset beiliegt)
        """
        if self.aktiver_kunde is None:
            return [], False

        kundennummer = self.aktiver_kunde.kundennummer
        album = self.kunden_repository.sticker_album(kundennummer)
        motive = sticker_modell.offene_motive(album, konfiguration.STICKER_PRO_EINKAUF)

        # So sieht das Album unmittelbar nach diesem Kauf aus.
        album_danach = dict(album)
        for motiv in motive:
            album_danach[motiv.schluessel] = 1

        starterset = starterset_modell.anspruch_besteht(
            anzahl_bestellungen=self.bestell_repository.anzahl_bestellungen(kundennummer) + 1,
            album=album_danach,
            bereits_erhalten=self.kunden_repository.starterset_erhalten(kundennummer),
        )
        return motive, starterset

    def sticker_album(self, kundennummer: int) -> dict[str, int]:
        """Das Sammelalbum eines Kunden - Motivschluessel auf Anzahl (/F53/)."""
        return self.kunden_repository.sticker_album(kundennummer)

    def starterset_vorschau(self) -> tuple[bool, bool]:
        """Wie steht es fuer den aktiven Kunden um das Starterset? (/F53/)

        Nur fuer die Anzeige in der Kasse - gebucht wird erst beim
        Kaufabschluss.

        :return: (schon erhalten, wuerde dieser Kauf es ausloesen)
        """
        if self.aktiver_kunde is None:
            return False, False

        bereits = self.kunden_repository.starterset_erhalten(
            self.aktiver_kunde.kundennummer
        )
        if bereits or self.warenkorb.ist_leer:
            return bereits, False

        _, faellig = self._praemien_bestimmen()
        return bereits, faellig

    def _bestand_erneut_pruefen(self) -> None:
        """Vergleicht jede Warenkorbposition mit dem aktuellen Lagerbestand.

        Der Unterstrich am Anfang bedeutet: nur zur internen Verwendung in
        dieser Klasse gedacht.
        """
        for position in self.warenkorb.positionen:
            aktueller_artikel = self.artikel_repository.laden(position.artikel.artikel_id)
            if aktueller_artikel is None:
                raise NichtGefundenFehler(
                    f"„{position.artikel.titel}“ existiert nicht mehr."
                )
            if position.menge > aktueller_artikel.lagerbestand:
                raise BestandsFehler(
                    f"Von „{aktueller_artikel.titel}“ sind nur noch "
                    f"{aktueller_artikel.lagerbestand} Stück auf Lager, "
                    f"im Warenkorb liegen {position.menge}."
                )
