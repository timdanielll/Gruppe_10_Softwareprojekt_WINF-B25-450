"""Warenkorb und Preisberechnung (/F11/, /F12/, /F13/).

Der Warenkorb ist die einzige Klasse des Programms, die **nicht** in der
Datenbank steht. Er existiert nur, solange ein Kunde bedient wird. Erst beim
Abschluss des Kaufs (/F14/) wird aus ihm eine Bestellung.

Die gesamte Rabattrechnung steht hier - und nur hier. Die GUI rechnet nie
selbst; sie fragt ``berechne()`` und zeigt an, was zurueckkommt.
"""

from fanshop import konfiguration
from fanshop.fehler import BestandsFehler, ValidierungsFehler
from fanshop.hilfsmittel import runde_geld
from fanshop.modelle.artikel import Artikel
from fanshop.modelle.sonderaktion import Sonderaktion


def positionsschluessel(artikel_id: int, groesse: str = "") -> str:
    """Baut den Schluessel einer Warenkorbzeile: Artikelnummer plus Groesse.

    Derselbe Pullover in Groesse M und in Groesse L sind zwei verschiedene
    Zeilen. Artikelnummer allein reicht als Kennung deshalb nicht mehr.
    """
    return f"{artikel_id}|{groesse or ''}"


class WarenkorbPosition:
    """Ein Artikel im Warenkorb - mit Menge und, bei Kleidung, mit Groesse."""

    def __init__(self, artikel: Artikel, menge: int, groesse: str = "") -> None:
        """Legt eine Warenkorbzeile an."""
        self.artikel = artikel
        self.menge = menge
        #: Gewaehlte Groesse; leer bei allem, was keine Groesse hat.
        self.groesse = groesse

    @property
    def schluessel(self) -> str:
        """Eindeutige Kennung dieser Zeile (Artikelnummer + Groesse)."""
        return positionsschluessel(self.artikel.artikel_id, self.groesse)

    @property
    def einzelpreis(self) -> float:
        """Preis pro Stueck nach Abzug des artikeleigenen Rabatts."""
        return self.artikel.endpreis

    @property
    def zeilensumme(self) -> float:
        """Menge mal Einzelpreis."""
        return runde_geld(self.menge * self.einzelpreis)

    @property
    def listenpreis_summe(self) -> float:
        """Menge mal Originalpreis - also ohne jeden Rabatt."""
        return runde_geld(self.menge * self.artikel.preis)

    @property
    def anzeigename(self) -> str:
        """Titel, bei Kleidung mit angehaengter Groesse."""
        if self.groesse:
            return f"{self.artikel.titel} (Gr. {self.groesse})"
        return self.artikel.titel

    def __str__(self) -> str:
        """Menge mal Anzeigename - z. B. '2 x Hoodie (Gr. L)'."""
        return f"{self.menge} x {self.anzeigename}"


class Preisuebersicht:
    """Das Ergebnis von :meth:`Warenkorb.berechne` - alle Zahlen einer Rechnung.

    Bewusst als eigene kleine Klasse und nicht als Zahlenwust: die GUI kann so
    jede Zeile der Summenanzeige einzeln beschriften, ohne selbst zu rechnen.
    """

    def __init__(
        self,
        listenwert: float = 0.0,
        artikelrabatt: float = 0.0,
        aktionsrabatt: float = 0.0,
        newsletter_rabatt: float = 0.0,
        aktionstitel: str = "",
    ) -> None:
        """Sammelt alle Einzelbetraege einer Rechnung."""
        self.listenwert = listenwert              # Summe aller Originalpreise
        self.artikelrabatt = artikelrabatt        # Summe der Artikelrabatte
        self.aktionsrabatt = aktionsrabatt        # Rabatt der aktiven Sonderaktion
        self.newsletter_rabatt = newsletter_rabatt  # einmalige 10 Prozent
        self.aktionstitel = aktionstitel          # Text fuer die Anzeige

    @property
    def zwischensumme(self) -> float:
        """Wert nach Artikelrabatten, aber vor Aktion und Newsletter."""
        return runde_geld(self.listenwert - self.artikelrabatt)

    @property
    def rabatt_gesamt(self) -> float:
        """Alle Rabatte zusammen."""
        return runde_geld(self.artikelrabatt + self.aktionsrabatt + self.newsletter_rabatt)

    @property
    def gesamtbetrag(self) -> float:
        """Der Betrag, den der Kunde zahlt."""
        return runde_geld(self.listenwert - self.rabatt_gesamt)

    def __str__(self) -> str:
        """Der Endbetrag als Text."""
        return f"Gesamtbetrag {self.gesamtbetrag:.2f} EUR"


class Warenkorb:
    """Sammelt Artikel fuer genau einen Kassiervorgang."""

    def __init__(self) -> None:
        """Startet mit einem leeren Korb."""
        self.positionen: list[WarenkorbPosition] = []

    # -- /F11/ Artikel hinzufuegen -----------------------------------------

    def hinzufuegen(self, artikel: Artikel, menge: int = 1, groesse: str = "") -> None:
        """Legt einen Artikel in den Warenkorb (/F11/).

        Bei Kleidung muss eine Groesse dabei sein - sie gehoert zur Zeile und
        entscheidet mit, ob eine Position erhoeht oder eine neue angelegt wird:
        derselbe Pullover in M und in L sind zwei Zeilen.

        Der Lagerbestand wird ueber **alle** Groessen eines Artikels gerechnet,
        weil das Lager je Artikel gefuehrt wird und nicht je Groesse.

        :raises ValidierungsFehler: bei Menge < 1 oder fehlender/falscher Groesse
        :raises BestandsFehler: wenn der Lagerbestand nicht ausreicht
        """
        if menge < 1:
            raise ValidierungsFehler("Die Menge muss mindestens 1 betragen.")

        gewaehlte_groesse = artikel.groesse_pruefen(groesse)

        vorhandene_position = self.position_zu(artikel.artikel_id, gewaehlte_groesse)
        bereits_im_korb = self.menge_von_artikel(artikel.artikel_id)
        neue_gesamtmenge = bereits_im_korb + menge

        if neue_gesamtmenge > artikel.lagerbestand:
            raise BestandsFehler(
                f"Von „{artikel.titel}“ sind nur noch {artikel.lagerbestand} Stück "
                f"auf Lager (im Warenkorb liegen bereits {bereits_im_korb})."
            )

        if vorhandene_position:
            vorhandene_position.menge += menge
        else:
            self.positionen.append(WarenkorbPosition(artikel, menge, gewaehlte_groesse))

    # -- /F12/ Artikel entfernen -------------------------------------------

    def entfernen(self, schluessel: str) -> None:
        """Loescht die Zeile mit diesem Schluessel aus dem Warenkorb (/F12/)."""
        self.positionen = [p for p in self.positionen if p.schluessel != schluessel]

    def menge_setzen(self, schluessel: str, menge: int) -> None:
        """Setzt die Menge einer Zeile neu (/F12/: "Reduzierung der Menge").

        Eine Menge von 0 entfernt die Zeile. Geprueft wird gegen den Bestand
        des Artikels ueber alle Groessen hinweg.
        """
        position = self.position_nach_schluessel(schluessel)
        if position is None:
            return
        if menge < 1:
            self.entfernen(schluessel)
            return

        andere_groessen = self.menge_von_artikel(position.artikel.artikel_id) - position.menge
        if andere_groessen + menge > position.artikel.lagerbestand:
            raise BestandsFehler(
                f"Von „{position.artikel.titel}“ sind nur noch "
                f"{position.artikel.lagerbestand} Stück auf Lager."
            )
        position.menge = menge

    def leeren(self) -> None:
        """Leert den Warenkorb - nach Kaufabschluss oder Kundenwechsel."""
        self.positionen = []

    # -- Abfragen ----------------------------------------------------------

    def position_zu(self, artikel_id: int, groesse: str = "") -> WarenkorbPosition | None:
        """Sucht die Zeile zu Artikel und Groesse - oder None."""
        return self.position_nach_schluessel(positionsschluessel(artikel_id, groesse))

    def position_nach_schluessel(self, schluessel: str) -> WarenkorbPosition | None:
        """Sucht die Zeile mit diesem Schluessel - oder None."""
        for position in self.positionen:
            if position.schluessel == schluessel:
                return position
        return None

    def menge_von_artikel(self, artikel_id: int) -> int:
        """Wie viele Stueck dieses Artikels liegen insgesamt im Korb?

        Zaehlt ueber alle Groessen, denn der Lagerbestand wird je Artikel
        gefuehrt und nicht je Groesse.
        """
        return sum(
            position.menge
            for position in self.positionen
            if position.artikel.artikel_id == artikel_id
        )

    @property
    def ist_leer(self) -> bool:
        """True, wenn nichts im Korb liegt."""
        return len(self.positionen) == 0

    @property
    def stueckzahl(self) -> int:
        """Gesamtzahl aller Stueck im Korb (nicht die Zahl der Positionen)."""
        return sum(position.menge for position in self.positionen)

    # -- /F13/ Bestellwert berechnen ---------------------------------------

    def berechne(
        self,
        sonderaktion: Sonderaktion | None = None,
        newsletter_rabatt_anwenden: bool = False,
    ) -> Preisuebersicht:
        """Berechnet den Bestellwert (/F13/).

        Die Rabatte werden in dieser festen Reihenfolge nacheinander
        abgezogen - jeder Schritt rechnet auf dem Ergebnis des vorherigen:

        1. **Artikelrabatt** je Position (``artikel.rabattsatz``)
        2. **Sonderaktion**: entweder auf die Positionen einer Kategorie
           oder auf die ganze Zwischensumme ab einem Mindestbestellwert
        3. **Newsletter-Willkommensrabatt** von 10 Prozent auf den Restbetrag

        Der Kunde bekommt dadurch nie mehr als 100 Prozent Rabatt, und die
        Reihenfolge ist immer dieselbe - unabhaengig davon, in welcher
        Reihenfolge die Artikel in den Korb gelegt wurden.
        """
        uebersicht = Preisuebersicht()

        # Schritt 1: Listenwert und Artikelrabatte
        uebersicht.listenwert = runde_geld(
            sum(position.listenpreis_summe for position in self.positionen)
        )
        zwischensumme = runde_geld(
            sum(position.zeilensumme for position in self.positionen)
        )
        uebersicht.artikelrabatt = runde_geld(uebersicht.listenwert - zwischensumme)

        # Schritt 2: Sonderaktion
        if sonderaktion is not None and sonderaktion.aktiv and zwischensumme > 0:
            if sonderaktion.art == Sonderaktion.ART_KATEGORIE:
                betroffener_umsatz = sum(
                    position.zeilensumme
                    for position in self.positionen
                    if sonderaktion.gilt_fuer_artikel(position.artikel)
                )
                if betroffener_umsatz > 0:
                    uebersicht.aktionsrabatt = runde_geld(
                        betroffener_umsatz * sonderaktion.rabattsatz
                    )
                    uebersicht.aktionstitel = sonderaktion.titel

            elif sonderaktion.gilt_fuer_bestellwert(zwischensumme):
                uebersicht.aktionsrabatt = runde_geld(
                    zwischensumme * sonderaktion.rabattsatz
                )
                uebersicht.aktionstitel = sonderaktion.titel

        # Schritt 3: Newsletter-Willkommensrabatt (/F52/)
        rest = runde_geld(zwischensumme - uebersicht.aktionsrabatt)
        if newsletter_rabatt_anwenden and rest > 0:
            uebersicht.newsletter_rabatt = runde_geld(
                rest * konfiguration.NEWSLETTER_RABATTSATZ
            )

        return uebersicht

    def __str__(self) -> str:
        """Kurzfassung: wie viele Zeilen und wie viele Stueck."""
        return f"Warenkorb mit {len(self.positionen)} Positionen ({self.stueckzahl} Stück)"
