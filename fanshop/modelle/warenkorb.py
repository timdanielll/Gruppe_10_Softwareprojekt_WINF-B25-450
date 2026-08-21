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


class WarenkorbPosition:
    """Ein Artikel im Warenkorb, zusammen mit der gewuenschten Menge."""

    def __init__(self, artikel: Artikel, menge: int) -> None:
        self.artikel = artikel
        self.menge = menge

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

    def __str__(self) -> str:
        return f"{self.menge} x {self.artikel.titel}"


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
        return runde_geld(self.artikelrabatt + self.aktionsrabatt + self.newsletter_rabatt)

    @property
    def gesamtbetrag(self) -> float:
        """Der Betrag, den der Kunde zahlt."""
        return runde_geld(self.listenwert - self.rabatt_gesamt)

    def __str__(self) -> str:
        return f"Gesamtbetrag {self.gesamtbetrag:.2f} EUR"


class Warenkorb:
    """Sammelt Artikel fuer genau einen Kassiervorgang."""

    def __init__(self) -> None:
        self.positionen: list[WarenkorbPosition] = []

    # -- /F11/ Artikel hinzufuegen -----------------------------------------

    def hinzufuegen(self, artikel: Artikel, menge: int = 1) -> None:
        """Legt einen Artikel in den Warenkorb.

        Ist der Artikel schon enthalten, wird die Menge erhoeht.
        Vor dem Hinzufuegen prueft das System den Lagerbestand (/F11/).

        :raises ValidierungsFehler: wenn die Menge kleiner als 1 ist
        :raises BestandsFehler: wenn der Lagerbestand nicht ausreicht
        """
        if menge < 1:
            raise ValidierungsFehler("Die Menge muss mindestens 1 betragen.")

        vorhandene_position = self.position_zu(artikel.artikel_id)
        bereits_im_korb = vorhandene_position.menge if vorhandene_position else 0
        neue_gesamtmenge = bereits_im_korb + menge

        if neue_gesamtmenge > artikel.lagerbestand:
            raise BestandsFehler(
                f"Von „{artikel.titel}“ sind nur noch {artikel.lagerbestand} Stück "
                f"auf Lager (im Warenkorb liegen bereits {bereits_im_korb})."
            )

        if vorhandene_position:
            vorhandene_position.menge = neue_gesamtmenge
        else:
            self.positionen.append(WarenkorbPosition(artikel, menge))

    # -- /F12/ Artikel entfernen -------------------------------------------

    def entfernen(self, artikel_id: int) -> None:
        """Loescht eine Position vollstaendig aus dem Warenkorb (/F12/)."""
        self.positionen = [p for p in self.positionen if p.artikel.artikel_id != artikel_id]

    def menge_setzen(self, artikel_id: int, menge: int) -> None:
        """Setzt die Menge einer Position neu (/F12/: "Reduzierung der Menge").

        Eine Menge von 0 entfernt die Position.
        """
        position = self.position_zu(artikel_id)
        if position is None:
            return
        if menge < 1:
            self.entfernen(artikel_id)
            return
        if menge > position.artikel.lagerbestand:
            raise BestandsFehler(
                f"Von „{position.artikel.titel}“ sind nur noch "
                f"{position.artikel.lagerbestand} Stück auf Lager."
            )
        position.menge = menge

    def leeren(self) -> None:
        """Leert den Warenkorb - nach Kaufabschluss oder Kundenwechsel."""
        self.positionen = []

    # -- Abfragen ----------------------------------------------------------

    def position_zu(self, artikel_id: int) -> WarenkorbPosition | None:
        for position in self.positionen:
            if position.artikel.artikel_id == artikel_id:
                return position
        return None

    @property
    def ist_leer(self) -> bool:
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
        return f"Warenkorb mit {len(self.positionen)} Positionen ({self.stueckzahl} Stück)"
