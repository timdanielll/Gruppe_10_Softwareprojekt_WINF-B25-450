"""Seite „Retouren" - Rückgabe im Ladenlokal (/F51/).

Links wird die Bestellung gesucht (Belegnummer oder Liste der letzten
Bestellungen), rechts werden ihre Positionen angezeigt und zurückgebucht.
"""

import customtkinter as ctk

from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine
from fanshop.gui.basis_seite import BasisSeite
from fanshop.gui.design import ABSTAND, farbe, schrift
from fanshop.hilfsmittel import euro, ganzzahl_aus_text


class RetourenSeite(BasisSeite):
    """Retouren-Terminal."""

    titel = "Retouren"

    def aufbauen(self) -> None:
        """Baut das Retourenterminal: Suche links, Buchung rechts."""
        self.aktuelle_bestellung = None
        #: Positionsnummer -> wie viele Stueck noch zurueckgegeben werden
        #: koennen. Die Positionsnummer und nicht die Artikelnummer, weil
        #: derselbe Artikel in zwei Groessen in einer Bestellung stehen kann.
        self.offene_mengen: dict[int, int] = {}

        self.inhalt.grid_columnconfigure(0, weight=3, uniform="retouren")
        self.inhalt.grid_columnconfigure(1, weight=2, uniform="retouren")
        self.inhalt.grid_rowconfigure(0, weight=1)

        self._suche_bauen()
        self._buchung_bauen()

    # ------------------------------------------------------------------

    def _suche_bauen(self) -> None:
        """Baut Belegsuche und Liste der letzten Bestellungen."""
        links = bausteine.Panel(self.inhalt, titel="1. Bestellung finden")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        suchzeile = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        suchzeile.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.nummer_feld = bausteine.Feld(
            suchzeile, "Bestellnummer vom Beleg", "z. B. 4", breite=180
        )
        self.nummer_feld.pack(side="left", anchor="n")
        self.nummer_feld.eingabe.bind("<Return>", lambda ereignis: self._bestellung_suchen())

        bausteine.knopf(suchzeile, "Suchen", self._bestellung_suchen, breite=120).pack(
            side="left", padx=(ABSTAND["sm"], 0), pady=(18, 0)
        )

        bausteine.Hinweis(
            links.inhalt,
            "Ohne Beleg: Bestellung in der Liste anklicken. Die Liste zeigt die "
            "50 neuesten Vorgänge.",
            umbruch=520,
        ).pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.bestell_tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Beleg", 60, "e"),
                ("Datum", 120, "w"),
                ("Kunde", 175, "w"),
                ("Betrag", 90, "e"),
            ],
            beim_waehlen=self._bestellung_aus_liste,
            leer_text="Es gibt noch keine Bestellungen.",
            hoehe=10,
        )
        self.bestell_tabelle.pack(fill="both", expand=True)

    # ------------------------------------------------------------------

    def _buchung_bauen(self) -> None:
        """Baut Positionstabelle, Mengenfeld und Retourenhistorie."""
        rechts = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        rechts.grid(row=0, column=1, sticky="nsew")

        positionsbereich = bausteine.Panel(rechts, titel="2. Position zurücknehmen")
        positionsbereich.pack(fill="both", expand=True, pady=(0, ABSTAND["md"]))

        self.beleginfo = bausteine.Hinweis(
            positionsbereich.inhalt, "Noch keine Bestellung geladen.", umbruch=350
        )
        self.beleginfo.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.positions_tabelle = bausteine.Tabelle(
            positionsbereich.inhalt,
            spalten=[
                ("Artikel", 115, "w"),
                ("Größe", 45, "w"),
                ("Gekauft", 55, "e"),
                ("Offen", 45, "e"),
                ("Einzel", 65, "e"),
            ],
            leer_text="Bitte links eine Bestellung wählen.",
            hoehe=6,
        )
        self.positions_tabelle.pack(fill="both", expand=True)

        buchungszeile = ctk.CTkFrame(positionsbereich.inhalt, fg_color="transparent")
        buchungszeile.pack(fill="x", pady=(ABSTAND["sm"], 0))

        self.menge_feld = bausteine.Feld(buchungszeile, "Retourenmenge", "1", breite=110)
        self.menge_feld.setzen("1")
        self.menge_feld.pack(side="left", anchor="n")

        bausteine.aktionsknopf(
            buchungszeile, "Retoure buchen", self._retoure_buchen, breite=220
        ).pack(side="left", padx=(ABSTAND["sm"], 0), pady=(18, 0))

        # -- bisherige Retouren ----------------------------------------
        historie = bausteine.Panel(rechts, titel="Bereits zurückgegeben")
        historie.pack(fill="x")

        self.retouren_tabelle = bausteine.Tabelle(
            historie.inhalt,
            spalten=[
                ("Artikel", 100, "w"),
                ("Größe", 45, "w"),
                ("Menge", 45, "e"),
                ("Datum", 95, "w"),
                ("Erstattet", 68, "e"),
            ],
            leer_text="Zu dieser Bestellung gibt es noch keine Retoure.",
            hoehe=4,
        )
        self.retouren_tabelle.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Daten
    # ------------------------------------------------------------------

    def beim_anzeigen(self) -> None:
        """Laedt die Bestellliste beim Oeffnen der Seite."""
        self._bestellliste_laden()
        if self.aktuelle_bestellung is not None:
            self._bestellung_anzeigen(self.aktuelle_bestellung.bestellnummer)

    def stil_aktualisieren(self) -> None:
        """Faerbt die Tabellen nach einem Moduswechsel neu."""
        self.bestell_tabelle.stil_anwenden()
        self.positions_tabelle.stil_anwenden()
        self.retouren_tabelle.stil_anwenden()

    def _bestellliste_laden(self) -> None:
        """Fuellt die Liste der 50 neuesten Bestellungen."""
        bestellungen = self.anwendung.retouren_service.letzte_bestellungen(50)
        zeilen = [
            (
                bestellung.bestellnummer,
                [
                    bestellung.bestellnummer,
                    bestellung.datum_text,
                    bestellung.kunde_anzeige,
                    euro(bestellung.gesamtbetrag),
                ],
            )
            for bestellung in bestellungen
        ]
        self.bestell_tabelle.fuellen(zeilen)

    def _bestellung_aus_liste(self) -> None:
        """Uebernimmt die in der Liste angeklickte Bestellung."""
        bestellnummer = self.bestell_tabelle.gewaehlter_schluessel()
        if bestellnummer is not None:
            self.nummer_feld.setzen(bestellnummer)
            self._bestellung_anzeigen(bestellnummer)

    def _bestellung_suchen(self) -> None:
        """Sucht die Bestellung zur eingetippten Belegnummer."""
        try:
            bestellnummer = ganzzahl_aus_text(self.nummer_feld.wert(), "Bestellnummer")
            self._bestellung_anzeigen(bestellnummer)
        except FanshopFehler as fehler:
            self.nummer_feld.fehler_zeigen(str(fehler))
            self.fehler_anzeigen(fehler)

    def _bestellung_anzeigen(self, bestellnummer: int) -> None:
        """Zeigt Kopfdaten, Positionen und offene Mengen einer Bestellung."""
        try:
            bestellung = self.anwendung.retouren_service.bestellung_suchen(bestellnummer)
        except FanshopFehler as fehler:
            self.nummer_feld.fehler_zeigen(str(fehler))
            self.fehler_anzeigen(fehler)
            return

        self.nummer_feld.fehler_loeschen()
        self.aktuelle_bestellung = bestellung
        self.melden(f"Bestellung {bestellung.bestellnummer} geladen.", art="neutral")

        self.beleginfo.configure(
            text=(
                f"Beleg {bestellung.bestellnummer} · {bestellung.datum_text} · "
                f"{bestellung.kunde_anzeige} · Gesamtbetrag {euro(bestellung.gesamtbetrag)}"
            )
        )

        zeilen = []
        markierungen = {}
        self.offene_mengen = {}
        for position in bestellung.positionen:
            offen = self.anwendung.retouren_service.offene_menge(
                position.position_id, position.menge
            )
            self.offene_mengen[position.position_id] = offen
            if offen == 0:
                # Vollstaendig zurueckgegeben: grau markieren statt beim Klick
                # eine Fehlermeldung aufzumachen.
                markierungen[position.position_id] = "erledigt"
            zeilen.append(
                (
                    position.position_id,
                    [
                        position.artikel_titel,
                        position.groesse or "–",
                        position.menge,
                        offen if offen else "zurück",
                        euro(position.historischer_preis),
                    ],
                )
            )
        self.positions_tabelle.fuellen(zeilen, markierungen=markierungen)
        self._retouren_anzeigen(bestellnummer)

    def _retouren_anzeigen(self, bestellnummer: int) -> None:
        """Fuellt die Liste der bereits gebuchten Retouren."""
        retouren = self.anwendung.retouren_service.retouren_zu(bestellnummer)
        zeilen = [
            (
                retoure.retouren_id,
                [
                    retoure.artikel_titel,
                    retoure.groesse or "–",
                    retoure.menge,
                    retoure.retouren_datum,
                    euro(retoure.erstattungsbetrag),
                ],
            )
            for retoure in retouren
        ]
        self.retouren_tabelle.fuellen(zeilen)

    # ------------------------------------------------------------------
    # /F51/ Retoure buchen
    # ------------------------------------------------------------------

    def _retoure_buchen(self) -> None:
        """Bucht die markierte Position zurueck ins Lager (/F51/)."""
        if self.aktuelle_bestellung is None:
            self.melden("Bitte zuerst links eine Bestellung wählen.", art="fehler")
            return

        position_id = self.positions_tabelle.gewaehlter_schluessel()
        if position_id is None:
            self.melden("Bitte die Zeile des Artikels anklicken.", art="fehler")
            return

        # Grau markierte Zeilen sind schon komplett zurueck - das sieht man,
        # deshalb genuegt hier eine Zeile in der Statusleiste.
        if self.offene_mengen.get(position_id) == 0:
            self.melden("Diese Position wurde bereits vollständig zurückgegeben.",
                        art="fehler")
            return

        try:
            menge = ganzzahl_aus_text(self.menge_feld.wert() or "1", "Retourenmenge")
            retoure = self.anwendung.retouren_service.retoure_buchen(
                self.aktuelle_bestellung.bestellnummer, position_id, menge
            )
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.menge_feld.setzen("1")
        self._bestellung_anzeigen(self.aktuelle_bestellung.bestellnummer)

        bausteine.Dialog(
            self,
            "Retoure gebucht",
            f"{retoure.menge} × „{retoure.anzeigename}“ wurde zurück ins Lager "
            f"gebucht.\n\nBitte {euro(retoure.erstattungsbetrag)} an den Kunden auszahlen.",
            art="erfolg",
            grosse_zahl=euro(retoure.erstattungsbetrag),
            ja_text="Erledigt",
        )
