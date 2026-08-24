"""Seite „Kasse" - der Kassiervorgang als geführte Strecke (/F11/–/F14/, /F52/, /F53/).

Das Pflichtenheft verlangt in /NF12/ einen „logischen, linearen Ablauf":

    Kunde wählen → Artikel auswählen → Rabatte prüfen → buchen → Sticker

Genau das ist diese Seite: vier Schritte, oben die Strecke, unten „Zurück" und
„Weiter". Auf jedem Schritt steht nur, was dort gebraucht wird — statt aller
vier Bereiche gleichzeitig auf einem Bildschirm.
"""

import customtkinter as ctk

from fanshop import konfiguration
from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine
from fanshop.gui.basis_seite import BasisSeite
from fanshop.gui.design import ABSTAND, farbe, schrift
from fanshop.hilfsmittel import euro, ganzzahl_aus_text, prozent, zahl_aus_text
from fanshop.modelle import starterset as starterset_modell
from fanshop.modelle import sticker as sticker_modell

ALLE_KATEGORIEN = "Alle Kategorien"

SCHRITT_KUNDE, SCHRITT_ARTIKEL, SCHRITT_KORB, SCHRITT_ABSCHLUSS = 0, 1, 2, 3


class KassenSeite(BasisSeite):
    """Die Hauptansicht: vier Schritte bis zum gebuchten Kauf."""

    titel = "Kasse"

    def aufbauen(self) -> None:
        self.schritt = SCHRITT_KUNDE
        self._suchauftrag = None

        # Kurzstand oben rechts: was liegt im Korb, was kostet es?
        self.korbstand = ctk.CTkLabel(
            self.kopfzeile,
            text="",
            font=schrift("zahl"),
            text_color=farbe("text_leise"),
            anchor="e",
        )
        self.korbstand.pack(side="right")

        self.schrittleiste = bausteine.Schrittleiste(
            self.inhalt,
            ["Kunde", "Artikel", "Warenkorb", "Abschluss"],
            beim_springen=self._schritt_angefordert,
        )
        self.schrittleiste.pack(fill="x", pady=(0, ABSTAND["md"]))

        self.buehne = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        self.buehne.pack(fill="both", expand=True)

        self.schritte = {
            SCHRITT_KUNDE: self._schritt_kunde_bauen(),
            SCHRITT_ARTIKEL: self._schritt_artikel_bauen(),
            SCHRITT_KORB: self._schritt_korb_bauen(),
            SCHRITT_ABSCHLUSS: self._schritt_abschluss_bauen(),
        }

        self._fussleiste_bauen()
        self.schritt_zeigen(SCHRITT_KUNDE)

    # ==================================================================
    # Schritt 1: Kunde
    # ==================================================================

    def _schritt_kunde_bauen(self) -> ctk.CTkFrame:
        rahmen = ctk.CTkFrame(self.buehne, fg_color="transparent")
        rahmen.grid_columnconfigure(0, weight=3, uniform="k1")
        rahmen.grid_columnconfigure(1, weight=2, uniform="k1")
        rahmen.grid_rowconfigure(0, weight=1)

        links = bausteine.Panel(rahmen, titel="Wer steht am Tresen?")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.kundensuche = bausteine.Feld(
            links.inhalt, "Kunde suchen", "Name oder Kundennummer", breite=320
        )
        self.kundensuche.pack(fill="x", pady=(0, ABSTAND["sm"]))
        self.kundensuche.eingabe.bind("<KeyRelease>", self._kundensuche_geplant)

        self.kunden_tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Nr.", 45, "e"),
                ("Name", 170, "w"),
                ("Ort", 120, "w"),
                ("Sticker", 65, "e"),
                ("Gutschein", 80, "w"),
            ],
            beim_waehlen=self._kunde_gewaehlt,
            beim_doppelklick=lambda: self.schritt_zeigen(SCHRITT_ARTIKEL),
            leer_text="Kein Kunde gefunden.",
            hoehe=9,
        )
        self.kunden_tabelle.pack(fill="both", expand=True)

        rechts = bausteine.Panel(rahmen, titel="Ausgewählt")
        rechts.grid(row=0, column=1, sticky="nsew")

        self.kunde_name = ctk.CTkLabel(
            rechts.inhalt, text="", font=schrift("titel"), text_color=farbe("text"),
            anchor="w", justify="left", wraplength=280,
        )
        self.kunde_name.pack(fill="x")

        self.kunde_details = bausteine.Hinweis(rechts.inhalt, "", umbruch=280)
        self.kunde_details.pack(fill="x", pady=(ABSTAND["xs"], ABSTAND["md"]))

        self.gutschein_kachel = ctk.CTkLabel(
            rechts.inhalt,
            text="",
            font=schrift("knopf"),
            text_color=farbe("rabatt"),
            anchor="w",
        )
        self.gutschein_kachel.pack(fill="x", pady=(0, ABSTAND["md"]))

        bausteine.knopf(
            rechts.inhalt, "Ohne Kundenkonto verkaufen", self._laufkundschaft, breite=260
        ).pack(fill="x")

        bausteine.Hinweis(
            rechts.inhalt,
            "Laufkundschaft: kein Sticker, kein Newsletter-Rabatt.",
            umbruch=280,
        ).pack(fill="x", pady=(ABSTAND["xs"], 0))

        return rahmen

    def _kundensuche_geplant(self, ereignis=None) -> None:
        if self._suchauftrag is not None:
            self.after_cancel(self._suchauftrag)
        self._suchauftrag = self.after(250, self._kunden_laden)

    def _kunden_laden(self) -> None:
        kunden = self.anwendung.kunden_service.suchen(self.kundensuche.wert())
        self.kunden_tabelle.fuellen(
            [
                (
                    kunde.kundennummer,
                    [
                        kunde.kundennummer,
                        kunde.name,
                        kunde.ort,
                        kunde.sticker_kontostand,
                        "offen" if kunde.darf_newsletter_rabatt_nutzen else "–",
                    ],
                )
                for kunde in kunden
            ]
        )
        aktiver = self.anwendung.kassen_service.aktiver_kunde
        if aktiver is not None:
            self.kunden_tabelle.auswahl_setzen(aktiver.kundennummer)

    def _kunde_gewaehlt(self) -> None:
        kundennummer = self.kunden_tabelle.gewaehlter_schluessel()
        if kundennummer is None:
            return
        try:
            kunde = self.anwendung.kassen_service.kunde_waehlen(kundennummer)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.kunde_name.configure(text=kunde.name)
        self.kunde_details.configure(
            text=f"Kundennummer {kunde.kundennummer}\n{kunde.anschrift}\n"
                 f"{kunde.sticker_kontostand} von {len(sticker_modell.MOTIVE)} "
                 f"Sammelstickern"
                 + (
                     f" · {starterset_modell.TITEL} erhalten"
                     if kunde.starterset_erhalten
                     else ""
                 )
        )
        self.gutschein_kachel.configure(
            text=(
                f"Newsletter-Gutschein über {prozent(konfiguration.NEWSLETTER_RABATTSATZ)} verfügbar"
                if kunde.darf_newsletter_rabatt_nutzen
                else ""
            )
        )
        self.melden(f"{kunde.name} ausgewählt.")
        self._korbstand_aktualisieren()

    def _laufkundschaft(self) -> None:
        self.anwendung.kassen_service.kunde_abwaehlen()
        self.kunden_tabelle.baum.selection_remove(*self.kunden_tabelle.baum.selection())
        self.kunde_name.configure(text="Laufkundschaft")
        self.kunde_details.configure(text="Verkauf ohne Kundenkonto.")
        self.gutschein_kachel.configure(text="")
        self.melden("Ohne Kundenkonto.", art="neutral")
        self.schritt_zeigen(SCHRITT_ARTIKEL)

    # ==================================================================
    # Schritt 2: Artikel
    # ==================================================================

    def _schritt_artikel_bauen(self) -> ctk.CTkFrame:
        rahmen = ctk.CTkFrame(self.buehne, fg_color="transparent")
        rahmen.grid_columnconfigure(0, weight=3, uniform="k2")
        rahmen.grid_columnconfigure(1, weight=2, uniform="k2")
        rahmen.grid_rowconfigure(0, weight=1)

        links = bausteine.Panel(rahmen, titel="Sortiment durchsuchen")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        zeile = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        zeile.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.suchfeld = bausteine.Feld(zeile, "Suche", "Titel oder Beschreibung", breite=210)
        self.suchfeld.pack(side="left", anchor="n", fill="x", expand=True)
        self.suchfeld.eingabe.bind("<KeyRelease>", self._suche_geplant)

        self.kategorie_auswahl = bausteine.Auswahlfeld(
            zeile,
            "Kategorie",
            [ALLE_KATEGORIEN, *konfiguration.KATEGORIEN],
            breite=160,
            beim_waehlen=lambda auswahl: self._artikel_laden(),
        )
        self.kategorie_auswahl.pack(side="left", padx=(ABSTAND["sm"], 0))

        zeile2 = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        zeile2.pack(fill="x", pady=(0, ABSTAND["sm"]))
        self.preis_von = bausteine.Feld(zeile2, "ab €", "0,00", breite=80)
        self.preis_von.pack(side="left", anchor="n")
        self.preis_bis = bausteine.Feld(zeile2, "bis €", "99,00", breite=80)
        self.preis_bis.pack(side="left", anchor="n", padx=(ABSTAND["sm"], 0))
        bausteine.knopf(zeile2, "Filtern", self._artikel_laden, breite=100).pack(
            side="left", padx=(ABSTAND["sm"], 0), pady=(20, 0)
        )
        bausteine.knopf(zeile2, "Zurücksetzen", self._filter_zuruecksetzen, breite=120).pack(
            side="left", padx=(ABSTAND["xs"], 0), pady=(20, 0)
        )

        self.artikel_tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Nr.", 45, "e"),
                ("Titel", 200, "w"),
                ("Kategorie", 95, "w"),
                ("Preis", 80, "e"),
                ("Bestand", 65, "e"),
            ],
            beim_waehlen=self._artikel_gewaehlt,
            beim_doppelklick=self._artikel_uebernehmen,
            leer_text="Keine Artikel gefunden. Filter zurücksetzen?",
            hoehe=8,
        )
        self.artikel_tabelle.pack(fill="both", expand=True)

        rechts = bausteine.Panel(rahmen, titel="Artikel")
        rechts.grid(row=0, column=1, sticky="nsew")

        self.bildkarte = bausteine.Bildkarte(rechts.inhalt)
        self.bildkarte.pack(fill="x")

        mengenzeile = ctk.CTkFrame(rechts.inhalt, fg_color="transparent")
        mengenzeile.pack(fill="x", pady=(ABSTAND["md"], 0))

        self.menge_feld = bausteine.Feld(mengenzeile, "Menge", "1", breite=90)
        self.menge_feld.setzen("1")
        self.menge_feld.pack(side="left", anchor="n")

        bausteine.aktionsknopf(
            mengenzeile, "In den Warenkorb", self._artikel_uebernehmen, breite=210
        ).pack(side="left", padx=(ABSTAND["sm"], 0), pady=(20, 0))

        bausteine.Hinweis(
            rechts.inhalt, "Doppelklick auf eine Zeile geht schneller.", umbruch=280
        ).pack(fill="x", pady=(ABSTAND["xs"], 0))

        return rahmen

    def _suche_geplant(self, ereignis=None) -> None:
        """Startet die Suche kurz nach dem letzten Tastendruck.

        Ohne diese Verzögerung liefe bei jedem einzelnen Buchstaben eine
        Datenbankabfrage.
        """
        if self._suchauftrag is not None:
            self.after_cancel(self._suchauftrag)
        self._suchauftrag = self.after(250, self._artikel_laden)

    def _artikel_laden(self) -> None:
        """Führt die Suche mit den aktuellen Filtern aus (/F23/)."""
        kategorie = self.kategorie_auswahl.wert()
        try:
            min_preis = zahl_aus_text(self.preis_von.wert(), "Preis ab") if self.preis_von.wert() else None
            max_preis = zahl_aus_text(self.preis_bis.wert(), "Preis bis") if self.preis_bis.wert() else None
            treffer = self.anwendung.artikel_service.suchen(
                suchtext=self.suchfeld.wert(),
                kategorie="" if kategorie == ALLE_KATEGORIEN else kategorie,
                min_preis=min_preis,
                max_preis=max_preis,
            )
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.preis_von.fehler_loeschen()
        self.preis_bis.fehler_loeschen()

        self.artikel_tabelle.fuellen(
            [
                (
                    artikel.artikel_id,
                    [
                        artikel.artikel_id,
                        artikel.titel,
                        artikel.kategorie,
                        euro(artikel.endpreis),
                        artikel.lagerbestand,
                    ],
                )
                for artikel in treffer
            ]
        )
        if self.artikel_tabelle.ist_leer:
            self.bildkarte.leeren("Kein Artikel gefunden.")
        else:
            self.artikel_tabelle.erste_waehlen()

    def _filter_zuruecksetzen(self) -> None:
        self.suchfeld.leeren()
        self.preis_von.leeren()
        self.preis_bis.leeren()
        self.kategorie_auswahl.setzen(ALLE_KATEGORIEN)
        self._artikel_laden()
        self.melden("Filter zurückgesetzt.", art="neutral")

    def _artikel_gewaehlt(self) -> None:
        artikel_id = self.artikel_tabelle.gewaehlter_schluessel()
        if artikel_id is None:
            return
        try:
            artikel = self.anwendung.artikel_service.laden(artikel_id)
        except FanshopFehler:
            return
        self.bildkarte.zeigen(artikel)

    def _artikel_uebernehmen(self) -> None:
        """Legt den markierten Artikel in den Warenkorb (/F11/)."""
        artikel_id = self.artikel_tabelle.gewaehlter_schluessel()
        if artikel_id is None:
            self.melden("Bitte zuerst einen Artikel auswählen.", art="fehler")
            return
        try:
            menge = ganzzahl_aus_text(self.menge_feld.wert() or "1", "Menge")
            self.anwendung.kassen_service.artikel_hinzufuegen(artikel_id, menge)
            artikel = self.anwendung.artikel_service.laden(artikel_id)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.menge_feld.setzen("1")
        self.melden(f"{menge} × {artikel.titel} in den Warenkorb.")
        self._korbstand_aktualisieren()

    # ==================================================================
    # Schritt 3: Warenkorb und Rabatte
    # ==================================================================

    def _schritt_korb_bauen(self) -> ctk.CTkFrame:
        rahmen = ctk.CTkFrame(self.buehne, fg_color="transparent")
        rahmen.grid_columnconfigure(0, weight=3, uniform="k3")
        rahmen.grid_columnconfigure(1, weight=2, uniform="k3")
        rahmen.grid_rowconfigure(0, weight=1)

        links = bausteine.Panel(rahmen, titel="Warenkorb")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.korb_tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Artikel", 210, "w"),
                ("Menge", 60, "e"),
                ("Einzel", 85, "e"),
                ("Summe", 90, "e"),
            ],
            leer_text="Noch nichts im Warenkorb.",
            hoehe=8,
        )
        self.korb_tabelle.pack(fill="both", expand=True)

        knoepfe = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        knoepfe.pack(fill="x", pady=(ABSTAND["sm"], 0))

        self.korb_menge = bausteine.Feld(knoepfe, "Neue Menge", "1", breite=90)
        self.korb_menge.setzen("1")
        self.korb_menge.pack(side="left", anchor="n")
        bausteine.knopf(knoepfe, "Menge setzen", self._menge_aendern, breite=130).pack(
            side="left", padx=(ABSTAND["sm"], 0), pady=(20, 0)
        )
        bausteine.knopf(knoepfe, "Entfernen", self._position_entfernen, breite=110).pack(
            side="left", padx=(ABSTAND["xs"], 0), pady=(20, 0)
        )
        bausteine.knopf(knoepfe, "Leeren", self._korb_leeren, breite=90).pack(
            side="left", padx=(ABSTAND["xs"], 0), pady=(20, 0)
        )

        rechts = bausteine.Panel(rahmen, titel="Rabatte")
        rechts.grid(row=0, column=1, sticky="nsew")

        self.aktions_hinweis = bausteine.Hinweis(rechts.inhalt, "", umbruch=280)
        self.aktions_hinweis.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.newsletter_haken = ctk.CTkCheckBox(
            rechts.inhalt,
            text=f"Newsletter-Rabatt anwenden ({prozent(konfiguration.NEWSLETTER_RABATTSATZ)})",
            font=schrift("text"),
            command=self._newsletter_umgeschaltet,
        )
        self.newsletter_haken.pack(anchor="w", pady=(0, ABSTAND["md"]))

        bausteine.Haarlinie(rechts.inhalt).pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.summenzeilen = ctk.CTkFrame(rechts.inhalt, fg_color="transparent")
        self.summenzeilen.pack(fill="x")

        return rahmen

    def _position_entfernen(self) -> None:
        """Entfernt die markierte Position vollständig (/F12/)."""
        artikel_id = self.korb_tabelle.gewaehlter_schluessel()
        if artikel_id is None:
            self.melden("Bitte eine Zeile im Warenkorb auswählen.", art="fehler")
            return
        self.anwendung.kassen_service.artikel_entfernen(artikel_id)
        self.melden("Position entfernt.")
        self._korb_anzeigen()

    def _menge_aendern(self) -> None:
        """Setzt die Menge der markierten Position neu (/F12/)."""
        artikel_id = self.korb_tabelle.gewaehlter_schluessel()
        if artikel_id is None:
            self.melden("Bitte eine Zeile im Warenkorb auswählen.", art="fehler")
            return
        try:
            menge = ganzzahl_aus_text(self.korb_menge.wert() or "1", "Menge")
            self.anwendung.kassen_service.menge_setzen(artikel_id, menge)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return
        self.melden(f"Menge auf {menge} gesetzt.")
        self._korb_anzeigen()

    def _korb_leeren(self) -> None:
        if self.anwendung.kassen_service.warenkorb.ist_leer:
            return
        if self.frage_stellen(
            "Warenkorb leeren?",
            "Alle Positionen werden entfernt. Der Vorgang wird nicht gebucht.",
            ja_text="Leeren",
        ):
            self.anwendung.kassen_service.warenkorb_leeren()
            self.melden("Warenkorb geleert.", art="neutral")
            self._korb_anzeigen()

    def _newsletter_umgeschaltet(self) -> None:
        try:
            self.anwendung.kassen_service.newsletter_rabatt_setzen(
                bool(self.newsletter_haken.get())
            )
        except FanshopFehler as fehler:
            self.newsletter_haken.deselect()
            self.fehler_anzeigen(fehler)
        self._korb_anzeigen()

    def _korb_anzeigen(self) -> None:
        """Zeichnet Warenkorb, Rabatte und Summen neu (/F13/)."""
        kasse = self.anwendung.kassen_service

        self.korb_tabelle.fuellen(
            [
                (
                    position.artikel.artikel_id,
                    [
                        position.artikel.titel,
                        position.menge,
                        euro(position.einzelpreis),
                        euro(position.zeilensumme),
                    ],
                )
                for position in kasse.warenkorb.positionen
            ]
        )

        aktion = kasse.aktive_sonderaktion()
        self.aktions_hinweis.configure(
            text=f"Aktive Sonderaktion: {aktion.titel}" if aktion else
                 "Zurzeit läuft keine Sonderaktion."
        )

        if kasse.newsletter_rabatt_moeglich() or kasse.newsletter_rabatt_anwenden:
            self.newsletter_haken.configure(state="normal")
        else:
            self.newsletter_haken.deselect()
            self.newsletter_haken.configure(state="disabled")

        self._summen_zeichnen(self.summenzeilen, kasse.preisuebersicht())
        self._korbstand_aktualisieren()

    def _summen_zeichnen(self, ziel: ctk.CTkFrame, uebersicht, gross: bool = True) -> None:
        """Zeichnet Zwischensumme, jede Rabattzeile einzeln und den Endbetrag."""
        for widget in ziel.winfo_children():
            widget.destroy()

        zeilen = [("Zwischensumme", uebersicht.listenwert, False)]
        if uebersicht.artikelrabatt > 0:
            zeilen.append(("Artikelrabatte", -uebersicht.artikelrabatt, True))
        if uebersicht.aktionsrabatt > 0:
            zeilen.append(
                (uebersicht.aktionstitel or "Sonderaktion", -uebersicht.aktionsrabatt, True)
            )
        if uebersicht.newsletter_rabatt > 0:
            zeilen.append(("Newsletter-Rabatt", -uebersicht.newsletter_rabatt, True))

        for beschriftung, betrag, ist_rabatt in zeilen:
            zeile = ctk.CTkFrame(ziel, fg_color="transparent")
            zeile.pack(fill="x", pady=1)
            ctk.CTkLabel(
                zeile,
                text=beschriftung,
                font=schrift("text_klein"),
                text_color=farbe("rabatt") if ist_rabatt else farbe("text_leise"),
                anchor="w",
                wraplength=170,
                justify="left",
            ).pack(side="left")
            ctk.CTkLabel(
                zeile,
                text=euro(betrag),
                font=schrift("zahl"),
                text_color=farbe("rabatt") if ist_rabatt else farbe("text"),
                anchor="e",
            ).pack(side="right")

        bausteine.Haarlinie(ziel).pack(fill="x", pady=ABSTAND["sm"])

        endzeile = ctk.CTkFrame(ziel, fg_color="transparent")
        endzeile.pack(fill="x")
        ctk.CTkLabel(
            endzeile, text="Zu zahlen", font=schrift("knopf"),
            text_color=farbe("text"), anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            endzeile,
            text=euro(uebersicht.gesamtbetrag),
            font=schrift("zahl_gross") if gross else schrift("zahl"),
            text_color=farbe("text"),
            anchor="e",
        ).pack(side="right")

    # ==================================================================
    # Schritt 4: Abschluss
    # ==================================================================

    def _schritt_abschluss_bauen(self) -> ctk.CTkFrame:
        rahmen = ctk.CTkFrame(self.buehne, fg_color="transparent")
        rahmen.grid_columnconfigure(0, weight=1, uniform="k4")
        rahmen.grid_columnconfigure(1, weight=1, uniform="k4")
        rahmen.grid_rowconfigure(0, weight=1)

        links = bausteine.Panel(rahmen, titel="Beleg prüfen")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.abschluss_kunde = ctk.CTkLabel(
            links.inhalt, text="", font=schrift("titel"), text_color=farbe("text"), anchor="w"
        )
        self.abschluss_kunde.pack(fill="x")

        self.abschluss_zeilen = bausteine.Hinweis(links.inhalt, "", umbruch=380)
        self.abschluss_zeilen.pack(fill="x", pady=(ABSTAND["xs"], ABSTAND["md"]))

        self.abschluss_summen = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        self.abschluss_summen.pack(fill="x")

        rechts = bausteine.Panel(rahmen, titel="Buchen")
        rechts.grid(row=0, column=1, sticky="nsew")

        bausteine.Hinweis(
            rechts.inhalt,
            "Mit dem Buchen entstehen Bestellung und Rechnung. Die Ware verlässt "
            "sofort das Lager (Mitnahmemodus), die Rechnung gilt als bezahlt.",
            umbruch=360,
        ).pack(fill="x", pady=(0, ABSTAND["md"]))

        self.sticker_vorschau = bausteine.Hinweis(rechts.inhalt, "", umbruch=360)
        self.sticker_vorschau.pack(fill="x", pady=(0, ABSTAND["md"]))

        bausteine.aktionsknopf(
            rechts.inhalt, "Kauf abschließen", self._kauf_abschliessen, breite=320
        ).pack(fill="x")

        return rahmen

    def _abschluss_anzeigen(self) -> None:
        kasse = self.anwendung.kassen_service
        korb = kasse.warenkorb

        self.abschluss_kunde.configure(
            text=kasse.aktiver_kunde.name if kasse.aktiver_kunde else "Laufkundschaft"
        )
        self.abschluss_zeilen.configure(
            text="\n".join(
                f"{p.menge} × {p.artikel.titel} — {euro(p.zeilensumme)}"
                for p in korb.positionen
            )
            or "Der Warenkorb ist leer."
        )
        self._summen_zeichnen(self.abschluss_summen, kasse.preisuebersicht())

        self.sticker_vorschau.configure(text=self._praemien_vorschau_text())

    def _praemien_vorschau_text(self) -> str:
        """Was dieser Kauf an Stickern und Sonderangebot bringt (/F53/).

        Steht vor dem Buchen im Schritt „Abschluss" — der Bediener soll dem
        Kunden ankündigen können, was gleich über den Tresen geht.
        """
        kasse = self.anwendung.kassen_service
        kunde = kasse.aktiver_kunde
        if kunde is None:
            return "Ohne Kundenkonto gibt es keine Sticker."

        offen = len(sticker_modell.offene_motive(
            kasse.sticker_album(kunde.kundennummer), konfiguration.STICKER_PRO_EINKAUF
        ))
        if offen == 0:
            zeile = f"{kunde.name} hat bereits alle Sammelsticker."
        elif offen == 1:
            zeile = f"Der letzte fehlende Sammelsticker geht an {kunde.name}."
        else:
            zeile = f"{offen} Sammelsticker gehen an {kunde.name}."

        erhalten, faellig = kasse.starterset_vorschau()
        if faellig:
            grund = "Damit ist die Sammlung voll" if offen else "Die Sammlung ist voll"
            zeile += (
                f"\nSonderangebot: {grund} — {starterset_modell.TITEL} mit "
                f"{starterset_modell.inhalt_text()} beilegen."
            )
        elif erhalten:
            zeile += f"\n{starterset_modell.TITEL} wurde bereits ausgegeben."
        return zeile

    def _kauf_abschliessen(self) -> None:
        kasse = self.anwendung.kassen_service
        try:
            beleg = kasse.kauf_abschliessen()
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self._sticker_dialog_zeigen(beleg)
        self.melden(
            f"Bestellung {beleg.bestellnummer} gebucht — {euro(beleg.uebersicht.gesamtbetrag)}."
        )

        # Nächster Kunde: zurück auf Schritt 1, Bestände neu laden.
        self._artikel_laden()
        self._kunden_laden()
        self._korb_anzeigen()
        self.schritt_zeigen(SCHRITT_KUNDE)

    def _sticker_dialog_zeigen(self, beleg) -> None:
        """Bestätigt den Kauf und zeigt die Sammelsticker (/F53/).

        Drei Fälle: kein Kundenkonto, ein Kauf mit neuen Stickern, oder ein
        Kauf ohne — weil die Sammlung schon voll ist. Liegt das Starterset bei,
        steht das in jedem Fall mit dabei.
        """
        kopf = (
            f"Bestellung {beleg.bestellnummer} über "
            f"{euro(beleg.uebersicht.gesamtbetrag)} ist gebucht und gilt als bezahlt."
        )

        if beleg.album_stand is None:
            bausteine.erfolg_zeigen(
                self,
                "Kauf abgeschlossen",
                f"{kopf}\n\nOhne Kundenkonto werden keine Sticker ausgegeben.",
            )
            return

        verschieden, gesamt = beleg.album_stand
        if beleg.motive:
            mitte = (
                f"Bitte diese {len(beleg.motive)} Sticker an {beleg.kundenname} "
                f"aushändigen. Sammlung: {verschieden} von {gesamt} Motiven."
            )
        else:
            mitte = (
                f"{beleg.kundenname} hat bereits alle {gesamt} Motive — "
                "es gibt keine weiteren Sticker."
            )

        nachricht = f"{kopf}\n\n{mitte}{self._starterset_zeile(beleg)}"
        bausteine.Dialog(
            self,
            "Kauf abgeschlossen",
            nachricht,
            art="erfolg",
            bilder=[motiv.pfad for motiv in beleg.motive],
            bild_beschriftungen=[motiv.titel for motiv in beleg.motive],
            ja_text="Erledigt",
        )

    @staticmethod
    def _starterset_zeile(beleg) -> str:
        """Der Hinweis auf das Sonderangebot - leer, wenn es keins gab (/F53/)."""
        if not beleg.starterset:
            return ""
        return (
            f"\n\nSonderangebot: Die Sammlung ist vollständig! "
            f"{starterset_modell.TITEL} mit {starterset_modell.inhalt_text()} "
            f"der Bestellung beilegen — es ist {beleg.kundenname} bereits "
            f"gutgeschrieben."
        )

    # ==================================================================
    # Strecke: Zurueck und Weiter
    # ==================================================================

    def _fussleiste_bauen(self) -> None:
        fuss = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        fuss.pack(fill="x", pady=(ABSTAND["md"], 0))

        self.zurueck_knopf = bausteine.knopf(fuss, "◂  Zurück", self._zurueck, breite=140)
        self.zurueck_knopf.pack(side="left")

        self.weiter_knopf = bausteine.knopf(fuss, "Weiter  ▸", self._weiter, breite=140)
        self.weiter_knopf.pack(side="right")

    def _zurueck(self) -> None:
        if self.schritt > SCHRITT_KUNDE:
            self.schritt_zeigen(self.schritt - 1)

    def _schritt_angefordert(self, ziel: int) -> None:
        """Sprung über die Schrittleiste.

        Zurück geht immer. Vorwärts wird Schritt für Schritt über dieselbe
        Prüfung geführt wie der Knopf „Weiter" - so kann man den Warenkorb
        nicht überspringen, aber vom Artikelschritt direkt auf „Abschluss"
        klicken, wenn schon Ware im Korb liegt.
        """
        if ziel <= self.schritt:
            self.schritt_zeigen(ziel)
            return

        while self.schritt < ziel:
            vorheriger = self.schritt
            self._weiter()
            if self.schritt == vorheriger:
                return          # ein Schritt hat blockiert und hat es gemeldet

    def _weiter(self) -> None:
        if self.schritt >= SCHRITT_ABSCHLUSS:
            return
        # Ohne Ware kein Warenkorb und kein Abschluss.
        if self.schritt == SCHRITT_ARTIKEL and self.anwendung.kassen_service.warenkorb.ist_leer:
            self.melden("Bitte zuerst einen Artikel in den Warenkorb legen.", art="fehler")
            return
        if self.schritt == SCHRITT_KORB and self.anwendung.kassen_service.warenkorb.ist_leer:
            self.melden("Der Warenkorb ist leer.", art="fehler")
            return
        self.schritt_zeigen(self.schritt + 1)

    def schritt_zeigen(self, nummer: int) -> None:
        """Blendet einen Schritt ein und lädt seine Daten."""
        self.schritt = nummer
        for schluessel, rahmen in self.schritte.items():
            if schluessel == nummer:
                rahmen.pack(fill="both", expand=True)
            else:
                rahmen.pack_forget()

        self.schrittleiste.setzen(nummer)

        if nummer == SCHRITT_KUNDE:
            self._kunden_laden()
        elif nummer == SCHRITT_ARTIKEL:
            self._artikel_laden()
        elif nummer == SCHRITT_KORB:
            self._korb_anzeigen()
        elif nummer == SCHRITT_ABSCHLUSS:
            self._abschluss_anzeigen()

        self.zurueck_knopf.configure(state="normal" if nummer > 0 else "disabled")
        self.weiter_knopf.configure(
            state="disabled" if nummer >= SCHRITT_ABSCHLUSS else "normal"
        )
        self._korbstand_aktualisieren()

    def _korbstand_aktualisieren(self) -> None:
        """Der Kurzstand oben rechts - damit der Korb nie aus dem Blick gerät."""
        kasse = self.anwendung.kassen_service
        korb = kasse.warenkorb
        if korb.ist_leer:
            self.korbstand.configure(text="Warenkorb leer")
            return
        uebersicht = kasse.preisuebersicht()
        self.korbstand.configure(
            text=f"{len(korb.positionen)} Artikel · {korb.stueckzahl} Stück · "
                 f"{euro(uebersicht.gesamtbetrag)}"
        )

    # ==================================================================

    def beim_anzeigen(self) -> None:
        self.schritt_zeigen(self.schritt)

    def stil_aktualisieren(self) -> None:
        self.artikel_tabelle.stil_anwenden()
        self.korb_tabelle.stil_anwenden()
        self.kunden_tabelle.stil_anwenden()
