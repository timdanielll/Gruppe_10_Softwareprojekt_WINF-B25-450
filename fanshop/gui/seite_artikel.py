"""Seite „Sortiment" - Artikelverwaltung (/F21/, /F22/, /F23/).

Links das gesamte Sortiment als Tabelle, rechts die Eingabemaske. Ein Klick in
die Tabelle füllt die Maske; der Knopf „Neu" leert sie wieder.
"""

import customtkinter as ctk

from fanshop import konfiguration
from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine, design
from fanshop.gui.basis_seite import BasisSeite
from fanshop.gui.design import ABSTAND, farbe, schrift
from fanshop.logik.artikel_service import OHNE_FOTO
from fanshop.hilfsmittel import euro, ganzzahl_aus_text, prozent, zahl_aus_text
from fanshop.modelle import starterset as starterset_modell

ALLE_KATEGORIEN = "Alle Kategorien"
OHNE_GROESSE = "–"


class ArtikelSeite(BasisSeite):
    """Sortiment anlegen, pflegen und durchsuchen."""

    titel = "Sortiment"

    def aufbauen(self) -> None:
        self.gewaehlte_artikel_id: int | None = None

        self.inhalt.grid_columnconfigure(0, weight=3, uniform="artikel")
        self.inhalt.grid_columnconfigure(1, weight=2, uniform="artikel")
        self.inhalt.grid_rowconfigure(0, weight=1)
        self.inhalt.grid_rowconfigure(1, weight=0)

        self._liste_bauen()
        self._maske_bauen()
        self._aktionen_bauen()

    # ------------------------------------------------------------------

    def _liste_bauen(self) -> None:
        links = bausteine.Panel(self.inhalt, titel="Sortiment")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        filterzeile = ctk.CTkFrame(links.inhalt, fg_color="transparent")
        filterzeile.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.suchfeld = bausteine.Feld(filterzeile, "Suche", "Titel oder Beschreibung", breite=200)
        self.suchfeld.pack(side="left", anchor="n")
        self.suchfeld.eingabe.bind("<Return>", lambda ereignis: self._liste_laden())

        self.kategorie_auswahl = bausteine.Auswahlfeld(
            filterzeile,
            "Kategorie",
            [ALLE_KATEGORIEN, *konfiguration.KATEGORIEN],
            breite=160,
            beim_waehlen=lambda auswahl: self._liste_laden(),
        )
        self.kategorie_auswahl.pack(side="left", padx=(ABSTAND["sm"], 0))

        bausteine.knopf(filterzeile, "Suchen", self._liste_laden, breite=110).pack(
            side="left", padx=(ABSTAND["sm"], 0), pady=(18, 0)
        )

        self.deaktivierte_zeigen = ctk.CTkCheckBox(
            links.inhalt,
            text="Deaktivierte Artikel mit anzeigen",
            font=schrift("text_klein"),
            command=self._liste_laden,
        )
        self.deaktivierte_zeigen.pack(anchor="w", pady=(0, ABSTAND["sm"]))

        self.tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Nr.", 40, "e"),
                ("Titel", 160, "w"),
                ("Kategorie", 92, "w"),
                ("Preis", 72, "e"),
                ("Bestand", 78, "e"),
                ("Status", 62, "w"),
            ],
            beim_waehlen=self._artikel_gewaehlt,
            leer_text="Keine Artikel gefunden. Filter zurücksetzen?",
            hoehe=7,
        )
        self.tabelle.pack(fill="both", expand=True)

    # ------------------------------------------------------------------

    def _maske_bauen(self) -> None:
        # rowspan=2: Die Maske laeuft ueber die volle Hoehe, damit unter ihr
        # nichts abgeschnitten wird. Die Sonderaktionen sitzen nur unter der Liste.
        rechts = bausteine.Panel(self.inhalt, titel="Artikel bearbeiten")
        rechts.grid(row=0, column=1, rowspan=2, sticky="nsew")

        # Die Knopfleiste wird ZUERST und mit side="bottom" gesetzt. Damit
        # reserviert pack ihren Platz am unteren Rand, bevor der Rest gefuellt
        # wird - die Knoepfe koennen dadurch nie aus dem Fenster rutschen.
        knopfzeile = ctk.CTkFrame(rechts.inhalt, fg_color="transparent")
        knopfzeile.pack(side="bottom", fill="x", pady=(ABSTAND["xs"], 0))
        bausteine.knopf(knopfzeile, "Speichern", self._speichern, breite=130).pack(side="left")
        bausteine.knopf(knopfzeile, "Neu", self._maske_leeren, breite=70).pack(
            side="left", padx=(ABSTAND["xs"], 0)
        )
        self.status_knopf = bausteine.gefahrenknopf(
            knopfzeile, "Deaktivieren", self._status_umschalten, breite=140
        )
        self.status_knopf.pack(side="left", padx=(ABSTAND["xs"], 0))

        bausteine.aktionsknopf(
            rechts.inhalt, "Artikel anlegen", self._anlegen, breite=260
        ).pack(side="bottom", fill="x", pady=(ABSTAND["sm"], 0))

        # Die Felder liegen in einem scrollbaren Bereich. Auf kleinen Bildschirmen
        # oder wenn spaeter ein Feld dazukommt, scrollt das Formular - die
        # Knoepfe darunter bleiben immer sichtbar und klickbar.
        formular = ctk.CTkScrollableFrame(rechts.inhalt, fg_color="transparent")
        formular.pack(side="top", fill="both", expand=True)

        self.bildkarte = bausteine.Bildkarte(formular)
        self.bildkarte.pack(fill="x", pady=(0, ABSTAND["sm"]))

        # Ein neuer Artikel hat kein Foto. Statt Dateien zu kopieren, waehlt man
        # hier eines der Bilder aus assets/artikel/ aus (/F21/).
        self.foto_auswahl = bausteine.Auswahlfeld(
            formular, "Produktfoto", [OHNE_FOTO], beim_waehlen=self._foto_gewaehlt
        )
        self.foto_auswahl.pack(fill="x", pady=(0, ABSTAND["md"]))
        self.bildliste: list[tuple[str, str | None]] = []

        self.titel_feld = bausteine.Feld(formular, "Titel", "z. B. Tasse htw saar")
        self.titel_feld.pack(fill="x", pady=(0, ABSTAND["sm"]))

        zeile1 = ctk.CTkFrame(formular, fg_color="transparent")
        zeile1.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.kategorie_feld = bausteine.Auswahlfeld(
            zeile1,
            "Kategorie",
            list(konfiguration.KATEGORIEN),
            breite=180,
            beim_waehlen=self._kategorie_gewechselt,
        )
        self.kategorie_feld.pack(side="left")

        self.groesse_feld = bausteine.Auswahlfeld(
            zeile1, "Größe", [OHNE_GROESSE, *konfiguration.GROESSEN], breite=110
        )
        self.groesse_feld.pack(side="left", padx=(ABSTAND["sm"], 0))

        zeile2 = ctk.CTkFrame(formular, fg_color="transparent")
        zeile2.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.preis_feld = bausteine.Feld(zeile2, "Preis (€)", "9,90", breite=100)
        self.preis_feld.pack(side="left", anchor="n")
        self.rabatt_feld = bausteine.Feld(zeile2, "Rabatt", "0,00", breite=120)
        self.rabatt_feld.pack(side="left", anchor="n", padx=(ABSTAND["sm"], 0))
        self.bestand_feld = bausteine.Feld(zeile2, "Bestand", "10", breite=110)
        self.bestand_feld.pack(side="left", anchor="n", padx=(ABSTAND["sm"], 0))

        ctk.CTkLabel(
            formular,
            text="BESCHREIBUNG",
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", pady=(ABSTAND["xs"], 2))
        self.beschreibung_feld = ctk.CTkTextbox(formular, height=80, font=schrift("text"))
        self.beschreibung_feld.pack(fill="x")

        # Kein weiterer Hinweistext: Der Knopf heisst "Deaktivieren" und die
        # Sicherheitsabfrage erklaert den Rest. Erklaertexte, die immer da sind,
        # liest nach dem zweiten Tag niemand mehr.

    # ------------------------------------------------------------------
    # Sonderaktionen (Lastenheft: "die aktiviert werden koennen")
    # ------------------------------------------------------------------

    def _aktionen_bauen(self) -> None:
        bereich = bausteine.Panel(self.inhalt, titel="Sonderaktionen")
        bereich.grid(
            row=1, column=0, sticky="nsew", padx=(0, ABSTAND["md"]), pady=(ABSTAND["md"], 0)
        )

        self.aktions_tabelle = bausteine.Tabelle(
            bereich.inhalt,
            spalten=[
                ("Titel", 250, "w"),
                ("Bedingung", 128, "w"),
                ("Rabatt", 65, "e"),
                ("Status", 60, "w"),
            ],
            leer_text="Keine Sonderaktionen hinterlegt.",
            hoehe=2,
        )
        self.aktions_tabelle.pack(fill="both", expand=True)

        knoepfe = ctk.CTkFrame(bereich.inhalt, fg_color="transparent")
        knoepfe.pack(fill="x", pady=(ABSTAND["sm"], 0))

        bausteine.knopf(knoepfe, "Aktion starten", self._aktion_starten, breite=150).pack(
            side="left"
        )
        bausteine.knopf(knoepfe, "Alle beenden", self._aktionen_beenden, breite=130).pack(
            side="left", padx=(ABSTAND["xs"], 0)
        )
        bausteine.Hinweis(
            knoepfe, "Höchstens eine Aktion gleichzeitig."
        ).pack(side="left", padx=(ABSTAND["md"], 0))

        # Das Starterset ist ein Dauerangebot und keine schaltbare Aktion:
        # Es kostet nichts extra, mindert keinen Preis und soll nicht
        # verschwinden, nur weil nebenbei ein Kategorierabatt laeuft. Deshalb
        # steht es hier als fester Hinweis unter der Tabelle (/F53/).
        bausteine.Hinweis(
            bereich.inhalt,
            f"Dauerhaftes Sonderangebot · {starterset_modell.TITEL}: "
            f"{starterset_modell.inhalt_text()} gratis "
            f"({starterset_modell.bedingung_text()}). "
            f"Läuft automatisch und ohne Mindestbestellwert.",
            umbruch=520,
        ).pack(fill="x", pady=(ABSTAND["sm"], 0))

    def _aktionen_laden(self) -> None:
        aktionen = self.anwendung.sonderaktion_service.alle()
        zeilen = []
        for aktion in aktionen:
            if aktion.art == aktion.ART_KATEGORIE:
                bedingung = f"Kategorie {aktion.zielkategorie}"
            else:
                bedingung = f"ab {euro(aktion.mindestbestellwert)}"
            zeilen.append(
                (
                    aktion.aktions_id,
                    [
                        aktion.titel,
                        bedingung,
                        prozent(aktion.rabattsatz),
                        "aktiv" if aktion.aktiv else "–",
                    ],
                )
            )
        self.aktions_tabelle.fuellen(zeilen)

    def _aktion_starten(self) -> None:
        aktions_id = self.aktions_tabelle.gewaehlter_schluessel()
        if aktions_id is None:
            self.melden("Bitte eine Sonderaktion auswählen.", art="fehler")
            return
        try:
            aktion = self.anwendung.sonderaktion_service.aktivieren(aktions_id)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return
        self._aktionen_laden()
        self.melden(f"Sonderaktion läuft: {aktion.titel}")

    def _aktionen_beenden(self) -> None:
        self.anwendung.sonderaktion_service.beenden()
        self._aktionen_laden()
        self.melden("Alle Sonderaktionen beendet.", art="neutral")

    # ------------------------------------------------------------------
    # Daten
    # ------------------------------------------------------------------

    def beim_anzeigen(self) -> None:
        self._bildliste_laden()
        self._liste_laden()
        self._aktionen_laden()

    def stil_aktualisieren(self) -> None:
        self.tabelle.stil_anwenden()
        self.aktions_tabelle.stil_anwenden()

    def _liste_laden(self) -> None:
        kategorie = self.kategorie_auswahl.wert()
        try:
            treffer = self.anwendung.artikel_service.suchen(
                suchtext=self.suchfeld.wert(),
                kategorie="" if kategorie == ALLE_KATEGORIEN else kategorie,
                nur_aktive=not bool(self.deaktivierte_zeigen.get()),
            )
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        zeilen = [
            (
                artikel.artikel_id,
                [
                    artikel.artikel_id,
                    artikel.titel,
                    artikel.kategorie,
                    euro(artikel.preis),
                    artikel.lagerbestand,
                    "aktiv" if artikel.aktiv else "deaktiviert",
                ],
            )
            for artikel in treffer
        ]
        self.tabelle.fuellen(zeilen)

        if self.gewaehlte_artikel_id is not None:
            self.tabelle.auswahl_setzen(self.gewaehlte_artikel_id)

    def _artikel_gewaehlt(self) -> None:
        artikel_id = self.tabelle.gewaehlter_schluessel()
        if artikel_id is None:
            return
        try:
            artikel = self.anwendung.artikel_service.laden(artikel_id)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.gewaehlte_artikel_id = artikel_id
        self.titel_feld.setzen(artikel.titel)
        self.kategorie_feld.setzen(artikel.kategorie)
        self.groesse_feld.setzen(getattr(artikel, "groesse", "") or OHNE_GROESSE)
        self.preis_feld.setzen(f"{artikel.preis:.2f}".replace(".", ","))
        self.rabatt_feld.setzen(f"{artikel.rabattsatz:.2f}".replace(".", ","))
        self.bestand_feld.setzen(artikel.lagerbestand)
        self.beschreibung_feld.delete("1.0", "end")
        self.beschreibung_feld.insert("1.0", artikel.beschreibung)

        self.bildkarte.zeigen(artikel)
        self.foto_auswahl.setzen(self._foto_bezeichnung(artikel.bildpfad))
        self.status_knopf.configure(
            text="Aktivieren" if not artikel.aktiv else "Deaktivieren"
        )
        self._kategorie_gewechselt(artikel.kategorie)

    def _bildliste_laden(self) -> None:
        """Fuellt die Fotoauswahl - Beschriftungen kommen aus dem Sortiment."""
        self.bildliste = self.anwendung.artikel_service.bildauswahl()
        self.foto_auswahl.auswahl.configure(
            values=[beschriftung for beschriftung, _ in self.bildliste]
        )

    def _gewaehltes_bild(self) -> str | None:
        """Dateiname des gewaehlten Fotos - oder None fuer "kein Foto"."""
        gewaehlt = self.foto_auswahl.wert()
        for beschriftung, datei in self.bildliste:
            if beschriftung == gewaehlt:
                return datei
        return None

    def _foto_bezeichnung(self, datei: str | None) -> str:
        for beschriftung, vorhandene in self.bildliste:
            if vorhandene == datei:
                return beschriftung
        return OHNE_FOTO

    def _foto_gewaehlt(self, auswahl: str = "") -> None:
        """Zeigt das gewaehlte Foto sofort in der Karte an."""
        datei = self._gewaehltes_bild()
        if datei is None:
            self.bildkarte.bildflaeche.configure(
                image=bausteine.leeres_bild(design.BILDGROESSE, design.BILDGROESSE),
                text="kein\nFoto",
            )
            return
        bild = bausteine.bild_laden(
            konfiguration.ARTIKELBILDER_VERZEICHNIS / datei,
            design.BILDGROESSE,
            design.BILDGROESSE,
        )
        self.bildkarte._bild_referenz = bild
        self.bildkarte.bildflaeche.configure(image=bild, text="")

    def _kategorie_gewechselt(self, kategorie: str) -> None:
        """Die Größe gibt es nur bei Damen und Herren."""
        if kategorie in konfiguration.KLEIDUNGS_KATEGORIEN:
            self.groesse_feld.auswahl.configure(state="normal")
        else:
            self.groesse_feld.setzen(OHNE_GROESSE)
            self.groesse_feld.auswahl.configure(state="disabled")

    def _maske_leeren(self) -> None:
        self.gewaehlte_artikel_id = None
        self.titel_feld.leeren()
        self.preis_feld.leeren()
        self.rabatt_feld.leeren()
        self.bestand_feld.leeren()
        self.beschreibung_feld.delete("1.0", "end")
        self.groesse_feld.setzen(OHNE_GROESSE)
        self.foto_auswahl.setzen(OHNE_FOTO)
        self.bildkarte.leeren("Neuer Artikel — noch kein Foto.")
        self.status_knopf.configure(text="Deaktivieren")

    # ------------------------------------------------------------------
    # Aktionen
    # ------------------------------------------------------------------

    def _werte_aus_maske(self) -> dict:
        """Liest die Maske aus und wandelt die Texte in Zahlen um."""
        groesse = self.groesse_feld.wert()
        return {
            "titel": self.titel_feld.wert(),
            "kategorie": self.kategorie_feld.wert(),
            "preis": zahl_aus_text(self.preis_feld.wert() or "0", "Preis"),
            "rabattsatz": zahl_aus_text(self.rabatt_feld.wert() or "0", "Rabattsatz"),
            "lagerbestand": ganzzahl_aus_text(self.bestand_feld.wert() or "0", "Lagerbestand"),
            "beschreibung": self.beschreibung_feld.get("1.0", "end").strip(),
            "groesse": "" if groesse == OHNE_GROESSE else groesse,
            "bildpfad": self._gewaehltes_bild(),
        }

    def _anlegen(self) -> None:
        """/F21/ Neuen Artikel anlegen."""
        try:
            werte = self._werte_aus_maske()
            artikel = self.anwendung.artikel_service.anlegen(**werte)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.gewaehlte_artikel_id = artikel.artikel_id
        self._liste_laden()
        self.melden(
            f"„{artikel.titel}“ angelegt (Nr. {artikel.artikel_id}) und sofort verkäuflich."
        )

    def _speichern(self) -> None:
        """/F22/ Änderungen am gewählten Artikel speichern."""
        if self.gewaehlte_artikel_id is None:
            self.melden(
                "Kein Artikel gewählt – bitte links anklicken oder neu anlegen.", art="fehler"
            )
            return
        try:
            werte = self._werte_aus_maske()
            artikel = self.anwendung.artikel_service.laden(self.gewaehlte_artikel_id)
            artikel.titel = werte["titel"]
            artikel.kategorie = werte["kategorie"]
            artikel.preis = werte["preis"]
            artikel.rabattsatz = werte["rabattsatz"]
            artikel.lagerbestand = werte["lagerbestand"]
            artikel.beschreibung = werte["beschreibung"]
            artikel.bildpfad = werte["bildpfad"]
            if hasattr(artikel, "groesse"):
                artikel.groesse = werte["groesse"]
            self.anwendung.artikel_service.aktualisieren(artikel)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self._liste_laden()
        self.melden(f"„{artikel.titel}“ gespeichert.")

    def _status_umschalten(self) -> None:
        """/F22/ Artikel deaktivieren oder wieder aktivieren."""
        if self.gewaehlte_artikel_id is None:
            return
        try:
            artikel = self.anwendung.artikel_service.laden(self.gewaehlte_artikel_id)
            if artikel.aktiv:
                if not self.frage_stellen(
                    "Artikel deaktivieren?",
                    f"„{artikel.titel}“ verschwindet aus dem Verkauf. "
                    "Alte Bestellungen bleiben erhalten.",
                    ja_text="Deaktivieren",
                ):
                    return
                self.anwendung.artikel_service.deaktivieren(artikel.artikel_id)
            else:
                self.anwendung.artikel_service.aktivieren(artikel.artikel_id)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self._liste_laden()
        self._artikel_gewaehlt()
