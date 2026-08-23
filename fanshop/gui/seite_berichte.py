"""Seite „Berichte" - Auswertungen für die Geschäftsführung.

Erfüllt /F31/, /F311/, /F312/, /F313/ (Muss) sowie /F24/, /F25/ (Muss) und die
Kann-Kriterien /F26/ und /F27/ (Diagramme).

Oben wird der Zeitraum gewählt, darunter stehen die Kennzahlen, unten die
Ranglisten. Die Diagramme öffnen sich in einem eigenen Fenster, damit die
Zahlentabellen sichtbar bleiben.
"""

import customtkinter as ctk

from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine, design
from fanshop.gui.basis_seite import BasisSeite
from fanshop.gui.design import ABSTAND, farbe, schrift
from fanshop.hilfsmittel import euro, heute_iso, zeitstempel_zu_text


class BerichteSeite(BasisSeite):
    """Kennzahlen, Ranglisten und Diagramme."""

    titel = "Berichte"

    def aufbauen(self) -> None:
        self.aktueller_bericht = None
        self.kennzahl_werte: dict[str, bausteine.Kachel] = {}

        self._zeitraum_bauen()
        self._kennzahlen_bauen()
        self._ranglisten_bauen()

    # ------------------------------------------------------------------

    def _zeitraum_bauen(self) -> None:
        bereich = bausteine.Panel(self.inhalt, titel="Zeitraum")
        bereich.pack(fill="x", pady=(0, ABSTAND["md"]))

        schnellwahl = ctk.CTkFrame(bereich.inhalt, fg_color="transparent")
        schnellwahl.pack(fill="x", pady=(0, ABSTAND["sm"]))

        for beschriftung, schluessel in [
            ("Gesamthistorie", "gesamt"),
            ("Letzter Tag", "tag"),
            ("Letzte Woche", "woche"),
            ("Letzter Monat", "monat"),
        ]:
            bausteine.knopf(
                schnellwahl,
                beschriftung,
                lambda s=schluessel: self._schnellwahl(s),
                breite=150,
            ).pack(side="left", padx=(0, ABSTAND["xs"]))

        datumszeile = ctk.CTkFrame(bereich.inhalt, fg_color="transparent")
        datumszeile.pack(fill="x")

        self.von_feld = bausteine.Feld(datumszeile, "Von (JJJJ-MM-TT)", "2026-08-01", breite=150)
        self.von_feld.pack(side="left", anchor="n")
        self.bis_feld = bausteine.Feld(datumszeile, "Bis (JJJJ-MM-TT)", heute_iso(), breite=150)
        self.bis_feld.pack(side="left", anchor="n", padx=(ABSTAND["sm"], 0))

        bausteine.aktionsknopf(
            datumszeile, "Bericht erstellen", self._bericht_aus_datum, breite=200
        ).pack(side="left", padx=(ABSTAND["md"], 0), pady=(18, 0))

        self.zeitraum_info = bausteine.Hinweis(bereich.inhalt, "")
        self.zeitraum_info.pack(fill="x", pady=(ABSTAND["sm"], 0))

        self.stammdaten_info = bausteine.Hinweis(bereich.inhalt, "")
        self.stammdaten_info.pack(fill="x", pady=(2, 0))

    # ------------------------------------------------------------------

    def _kennzahlen_bauen(self) -> None:
        bereich = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        bereich.pack(fill="x", pady=(0, ABSTAND["md"]))

        kennzahlen = [
            ("anzahl_bestellungen", "Bestellungen", "/F311/"),
            ("umsatz", "Umsatz", "/F312/"),
            ("erstattungen", "Erstattungen", "Retouren"),
            ("nettoumsatz", "Nettoumsatz", "Umsatz − Erstattungen"),
        ]
        for spalte, (schluessel, beschriftung, zusatz) in enumerate(kennzahlen):
            bereich.grid_columnconfigure(spalte, weight=1, uniform="kennzahl")

            kachel = bausteine.Kachel(bereich, beschriftung, zusatz)
            kachel.grid(
                row=0,
                column=spalte,
                sticky="nsew",
                padx=(0 if spalte == 0 else ABSTAND["sm"], 0),
            )
            self.kennzahl_werte[schluessel] = kachel

    # ------------------------------------------------------------------

    def _ranglisten_bauen(self) -> None:
        """Die drei Auswertungstabellen stehen nebeneinander.

        Untereinander wuerden sie nicht auf einen 800 Pixel hohen Bildschirm
        passen - und eine Auswertung, fuer die man scrollen muss, sieht sich
        niemand an.
        """
        # Eine Reihe fuer die Diagramme (/F26/, /F27/) - gehoert zu allen drei
        # Tabellen, deshalb steht sie ueber ihnen und nicht in einem Panel.
        diagrammzeile = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        diagrammzeile.pack(fill="x", pady=(0, ABSTAND["md"]))

        ctk.CTkLabel(
            diagrammzeile,
            text="DIAGRAMME",
            font=schrift("label"),
            text_color=farbe("text_leise"),
        ).pack(side="left", padx=(0, ABSTAND["sm"]))

        for beschriftung, befehl in [
            ("Umsatz je Kategorie", self._diagramm_kategorien),
            ("Umsatzstärkste Artikel", self._diagramm_umsatz),
            ("Häufigste Artikel", self._diagramm_haeufigkeit),
        ]:
            bausteine.knopf(diagrammzeile, beschriftung, befehl, breite=210).pack(
                side="left", padx=(0, ABSTAND["xs"])
            )

        bereich = ctk.CTkFrame(self.inhalt, fg_color="transparent")
        bereich.pack(fill="both", expand=True)
        bereich.grid_columnconfigure(0, weight=3, uniform="bericht")
        bereich.grid_columnconfigure(1, weight=2, uniform="bericht")
        bereich.grid_columnconfigure(2, weight=2, uniform="bericht")
        bereich.grid_rowconfigure(0, weight=1)

        # -- /F313/ Umsatzanteile --------------------------------------
        links = bausteine.Panel(bereich, titel="Umsatzanteile im Zeitraum")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.anteil_tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Artikel", 165, "w"),
                ("Menge", 50, "e"),
                ("Umsatz", 70, "e"),
                ("Anteil", 55, "e"),
            ],
            leer_text="Im gewählten Zeitraum wurde nichts verkauft.",
            hoehe=6,
        )
        self.anteil_tabelle.pack(fill="both", expand=True)

        # -- /F24/ Umsatzstärkste --------------------------------------
        mitte = bausteine.Panel(bereich, titel="Umsatzstärkste Artikel")
        mitte.grid(row=0, column=1, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.umsatz_tabelle = bausteine.Tabelle(
            mitte.inhalt,
            spalten=[("Artikel", 140, "w"), ("Umsatz", 70, "e")],
            leer_text="Noch keine Verkäufe.",
            hoehe=6,
        )
        self.umsatz_tabelle.pack(fill="both", expand=True)

        # -- /F25/ Häufigste -------------------------------------------
        rechts = bausteine.Panel(bereich, titel="Am häufigsten gekauft")
        rechts.grid(row=0, column=2, sticky="nsew")

        self.haeufig_tabelle = bausteine.Tabelle(
            rechts.inhalt,
            spalten=[("Artikel", 140, "w"), ("Vorgänge", 65, "e")],
            leer_text="Noch keine Verkäufe.",
            hoehe=6,
        )
        self.haeufig_tabelle.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Daten
    # ------------------------------------------------------------------

    def beim_anzeigen(self) -> None:
        """Beim Öffnen der Seite wird die Gesamthistorie gezeigt."""
        self._schnellwahl("gesamt")
        self._ranglisten_laden()

    def stil_aktualisieren(self) -> None:
        self.anteil_tabelle.stil_anwenden()
        self.umsatz_tabelle.stil_anwenden()
        self.haeufig_tabelle.stil_anwenden()

    def _schnellwahl(self, auswahl: str) -> None:
        try:
            von, bis = self.anwendung.bericht_service.zeitraum_schnellwahl(auswahl)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return
        self._bericht_anzeigen(von, bis)

    def _bericht_aus_datum(self) -> None:
        try:
            von, bis = self.anwendung.bericht_service.zeitraum_aus_datum(
                self.von_feld.wert(), self.bis_feld.wert()
            )
        except FanshopFehler as fehler:
            self.von_feld.fehler_zeigen(str(fehler))
            self.fehler_anzeigen(fehler)
            return
        self.von_feld.fehler_loeschen()
        self._bericht_anzeigen(von, bis)

    def _bericht_anzeigen(self, von: int, bis: int) -> None:
        bericht = self.anwendung.bericht_service.bericht_erstellen(von, bis)
        self.aktueller_bericht = bericht

        self.zeitraum_info.configure(
            text=f"Ausgewertet: {zeitstempel_zu_text(von)} bis {zeitstempel_zu_text(bis)}"
        )
        self.stammdaten_info.configure(
            text=f"Stammdaten: {self.anwendung.artikel_repository.anzahl()} Artikel · "
                 f"{self.anwendung.kunden_repository.anzahl()} Kunden"
        )

        self.kennzahl_werte["anzahl_bestellungen"].setzen(
            str(bericht.kennzahlen["anzahl_bestellungen"])
        )
        self.kennzahl_werte["umsatz"].setzen(euro(bericht.kennzahlen["umsatz"]))
        self.kennzahl_werte["erstattungen"].setzen(euro(bericht.kennzahlen["erstattungen"]))
        self.kennzahl_werte["nettoumsatz"].setzen(euro(bericht.kennzahlen["nettoumsatz"]))
        self.melden(
            f"Bericht erstellt: {bericht.anzahl_bestellungen} Bestellungen.", art="neutral"
        )

        zeilen = [
            (
                eintrag["artikel_id"],
                [
                    eintrag["titel"],
                    eintrag["menge"],
                    euro(eintrag["umsatz"]),
                    f"{eintrag['anteil'] * 100:.1f} %".replace(".", ","),
                ],
            )
            for eintrag in bericht.umsatzanteile
        ]
        self.anteil_tabelle.fuellen(zeilen)

    def _ranglisten_laden(self) -> None:
        """/F24/ und /F25/ - beziehen sich immer auf die Gesamthistorie."""
        umsatz = self.anwendung.artikel_service.umsatzstaerkste(10)
        self.umsatz_tabelle.fuellen(
            [
                (e["artikel_id"], [e["titel"], euro(e["umsatz"])])
                for e in umsatz
            ]
        )

        haeufig = self.anwendung.artikel_service.haeufigste(10)
        self.haeufig_tabelle.fuellen(
            [(e["artikel_id"], [e["titel"], e["vorgaenge"]]) for e in haeufig]
        )

    # ------------------------------------------------------------------
    # /F26/ und /F27/ Diagramme (Kann-Kriterien)
    # ------------------------------------------------------------------

    def _diagramm_umsatz(self) -> None:
        daten = self.anwendung.artikel_service.umsatzstaerkste(8)
        self._balkendiagramm_zeigen(
            titel="Umsatzstärkste Artikel",
            beschriftungen=[e["titel"] for e in daten],
            werte=[e["umsatz"] for e in daten],
            achsentitel="Umsatz in €",
        )

    def _diagramm_haeufigkeit(self) -> None:
        daten = self.anwendung.artikel_service.haeufigste(8)
        self._balkendiagramm_zeigen(
            titel="Am häufigsten gekaufte Artikel",
            beschriftungen=[e["titel"] for e in daten],
            werte=[e["vorgaenge"] for e in daten],
            achsentitel="Anzahl Verkaufsvorgänge",
        )

    def _diagramm_kategorien(self) -> None:
        if self.aktueller_bericht is None:
            return
        daten = self.aktueller_bericht.umsatz_je_kategorie
        self._balkendiagramm_zeigen(
            titel="Umsatz je Kategorie",
            beschriftungen=[e["kategorie"] for e in daten],
            werte=[e["umsatz"] for e in daten],
            achsentitel="Umsatz in €",
        )

    def _balkendiagramm_zeigen(
        self, titel: str, beschriftungen: list[str], werte: list[float], achsentitel: str
    ) -> None:
        """Öffnet ein Fenster mit einem waagerechten Balkendiagramm.

        matplotlib wird erst hier importiert. Fehlt die Bibliothek, läuft der
        Rest der Anwendung trotzdem - es erscheint nur ein Hinweis.
        """
        if not werte:
            self.hinweis_anzeigen(
                "Keine Daten",
                "Für diese Auswertung gibt es im gewählten Zeitraum noch keine Verkäufe.",
            )
            return

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except ImportError:
            self.hinweis_anzeigen(
                "matplotlib fehlt",
                "Für die Diagramme wird matplotlib benötigt:\n\n"
                "pip install -r requirements.txt",
            )
            return

        fenster = ctk.CTkToplevel(self)
        fenster.title(titel)
        fenster.geometry("860x520")
        fenster.configure(fg_color=farbe("karton"))
        fenster.transient(self.winfo_toplevel())

        papier = design.einzelfarbe("karton")
        text = design.einzelfarbe("text")
        gold = design.einzelfarbe("akzent")
        linie = design.einzelfarbe("linie")

        abbildung = Figure(figsize=(8.4, 4.8), dpi=100, facecolor=papier)
        achse = abbildung.add_subplot(111, facecolor=papier)

        # Größter Wert oben: dafür die Reihenfolge umdrehen.
        achse.barh(list(reversed(beschriftungen)), list(reversed(werte)), color=gold)
        achse.set_xlabel(achsentitel, color=text, fontsize=9)
        achse.set_title(titel, color=text, fontsize=12, loc="left")
        achse.tick_params(colors=text, labelsize=8)
        for rand in ("top", "right", "left"):
            achse.spines[rand].set_visible(False)
        achse.spines["bottom"].set_color(linie)
        achse.xaxis.grid(True, color=linie, linewidth=0.8)
        achse.set_axisbelow(True)
        abbildung.tight_layout()

        leinwand = FigureCanvasTkAgg(abbildung, master=fenster)
        leinwand.draw()
        leinwand.get_tk_widget().pack(fill="both", expand=True, padx=ABSTAND["md"], pady=ABSTAND["md"])

        bausteine.knopf(fenster, "Schließen", fenster.destroy, breite=140).pack(
            pady=(0, ABSTAND["md"])
        )
        fenster.bind("<Escape>", lambda ereignis: fenster.destroy())
