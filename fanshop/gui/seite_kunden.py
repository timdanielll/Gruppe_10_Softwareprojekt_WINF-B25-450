"""Seite „Kunden" - Kundenkartei (/F41/ bis /F44/, /F52/, /F53/).

Links die Kartei mit Echtzeitsuche, rechts die Stammdatenmaske samt
Newsletter-Anmeldung, Sammelalbum und Starterset-Stand.
"""

import customtkinter as ctk

from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine
from fanshop.gui.basis_seite import BasisSeite
from fanshop.gui.design import ABSTAND, farbe, schrift
from fanshop.hilfsmittel import ganzzahl_aus_text, prozent
from fanshop import konfiguration
from fanshop.modelle import starterset as starterset_modell
from fanshop.modelle import sticker as sticker_modell


class KundenSeite(BasisSeite):
    """Kunden anlegen, suchen, pflegen und löschen."""

    titel = "Kunden"

    def aufbauen(self) -> None:
        self.gewaehlte_kundennummer: int | None = None
        self._suchauftrag = None

        self.inhalt.grid_columnconfigure(0, weight=3, uniform="kunden")
        self.inhalt.grid_columnconfigure(1, weight=2, uniform="kunden")
        self.inhalt.grid_rowconfigure(0, weight=1)

        self._liste_bauen()
        self._maske_bauen()

    # ------------------------------------------------------------------

    def _liste_bauen(self) -> None:
        links = bausteine.Panel(self.inhalt, titel="Kundenkartei")
        links.grid(row=0, column=0, sticky="nsew", padx=(0, ABSTAND["md"]))

        self.suchfeld = bausteine.Feld(
            links.inhalt, "Suche nach Name oder Kundennummer", "z. B. Becker oder 3", breite=300
        )
        self.suchfeld.pack(fill="x", pady=(0, ABSTAND["sm"]))
        self.suchfeld.eingabe.bind("<KeyRelease>", self._suche_geplant)

        self.tabelle = bausteine.Tabelle(
            links.inhalt,
            spalten=[
                ("Nr.", 45, "e"),
                ("Name", 175, "w"),
                ("Straße", 175, "w"),
                ("PLZ", 60, "e"),
                ("Ort", 130, "w"),
            ],
            beim_waehlen=self._kunde_gewaehlt,
            leer_text="Keine Kunden gefunden. Suchfeld leeren?",
            hoehe=10,
        )
        self.tabelle.pack(fill="both", expand=True)

    # ------------------------------------------------------------------

    def _maske_bauen(self) -> None:
        rechts = bausteine.Panel(self.inhalt, titel="Kundendaten")
        rechts.grid(row=0, column=1, sticky="nsew")

        # Erst die Knoepfe mit side="bottom": pack reserviert ihren Platz am
        # unteren Rand, bevor der Rest gefuellt wird. Sie koennen dadurch nie
        # aus dem Fenster rutschen, egal wie lang das Formular wird.
        bausteine.gefahrenknopf(
            rechts.inhalt, "Kunde löschen", self._loeschen, breite=180
        ).pack(side="bottom", anchor="w", pady=(ABSTAND["xs"], 0))

        knopfzeile = ctk.CTkFrame(rechts.inhalt, fg_color="transparent")
        knopfzeile.pack(side="bottom", fill="x", pady=(ABSTAND["xs"], 0))
        bausteine.knopf(knopfzeile, "Änderungen speichern", self._speichern, breite=190).pack(
            side="left"
        )
        bausteine.knopf(knopfzeile, "Neu", self._maske_leeren, breite=80).pack(
            side="left", padx=(ABSTAND["xs"], 0)
        )

        bausteine.aktionsknopf(
            rechts.inhalt, "Kunde anlegen", self._anlegen, breite=260
        ).pack(side="bottom", fill="x", pady=(ABSTAND["sm"], 0))

        # Die Felder liegen in einem scrollbaren Bereich - bei wenig Platz
        # scrollt das Formular, die Knoepfe darunter bleiben sichtbar.
        formular = ctk.CTkScrollableFrame(rechts.inhalt, fg_color="transparent")
        formular.pack(side="top", fill="both", expand=True)

        self.name_feld = bausteine.Feld(formular, "Name", "Vorname Nachname")
        self.name_feld.pack(fill="x", pady=(0, ABSTAND["sm"]))

        self.strasse_feld = bausteine.Feld(formular, "Straße und Hausnummer", "Waldhausweg 14")
        self.strasse_feld.pack(fill="x", pady=(0, ABSTAND["sm"]))

        zeile = ctk.CTkFrame(formular, fg_color="transparent")
        zeile.pack(fill="x", pady=(0, ABSTAND["md"]))
        self.plz_feld = bausteine.Feld(zeile, "PLZ", "66117", breite=90)
        self.plz_feld.pack(side="left", anchor="n")
        self.ort_feld = bausteine.Feld(zeile, "Ort", "Saarbrücken", breite=200)
        self.ort_feld.pack(side="left", anchor="n", padx=(ABSTAND["sm"], 0))

        bausteine.Haarlinie(formular).pack(fill="x", pady=(0, ABSTAND["md"]))

        # -- Newsletter (/F52/) und Sammelalbum (/F53/) ----------------
        ctk.CTkLabel(
            formular,
            text="NEWSLETTER, STICKER UND SONDERANGEBOT",
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", pady=(0, ABSTAND["xs"]))

        self.newsletter_haken = ctk.CTkCheckBox(
            formular,
            text=f"Newsletter · {prozent(konfiguration.NEWSLETTER_RABATTSATZ)} Willkommensrabatt",
            font=schrift("text"),
            command=self._newsletter_umgeschaltet,
        )
        self.newsletter_haken.pack(anchor="w", pady=(0, ABSTAND["xs"]))

        self.gutschein_info = bausteine.Hinweis(formular, "", umbruch=340)
        self.gutschein_info.pack(fill="x")

        stickerzeile = ctk.CTkFrame(formular, fg_color="transparent")
        stickerzeile.pack(fill="x", pady=(ABSTAND["sm"], ABSTAND["xs"]))
        ctk.CTkLabel(
            stickerzeile,
            text="Sammelsticker",
            font=schrift("text"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(side="left")
        self.sticker_label = ctk.CTkLabel(
            stickerzeile,
            text="0",
            font=schrift("zahl_gross"),
            text_color=farbe("text"),
            anchor="e",
        )
        self.sticker_label.pack(side="right")

        self.album = bausteine.StickerAlbum(formular)
        self.album.pack(fill="x", pady=(0, ABSTAND["xs"]))

        # Das Starterset-Sonderangebot (/F53/) - siehe modelle/starterset.py.
        self.starterset_info = bausteine.Hinweis(formular, "", umbruch=340)
        self.starterset_info.pack(fill="x", pady=(0, ABSTAND["sm"]))

    # ------------------------------------------------------------------
    # Daten
    # ------------------------------------------------------------------

    def beim_anzeigen(self) -> None:
        self._liste_laden()

    def stil_aktualisieren(self) -> None:
        self.tabelle.stil_anwenden()

    def _suche_geplant(self, ereignis=None) -> None:
        """Echtzeitsuche (/F44/) - startet kurz nach dem letzten Tastendruck."""
        if self._suchauftrag is not None:
            self.after_cancel(self._suchauftrag)
        self._suchauftrag = self.after(250, self._liste_laden)

    def _liste_laden(self) -> None:
        kunden = self.anwendung.kunden_service.suchen(self.suchfeld.wert())
        zeilen = [
            (
                kunde.kundennummer,
                [
                    kunde.kundennummer,
                    kunde.name,
                    kunde.strasse,
                    kunde.plz_text,
                    kunde.ort,
                ],
            )
            for kunde in kunden
        ]
        self.tabelle.fuellen(zeilen)

        if self.gewaehlte_kundennummer is not None:
            self.tabelle.auswahl_setzen(self.gewaehlte_kundennummer)

    def _kunde_gewaehlt(self) -> None:
        kundennummer = self.tabelle.gewaehlter_schluessel()
        if kundennummer is None:
            return
        try:
            kunde = self.anwendung.kunden_service.laden(kundennummer)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.gewaehlte_kundennummer = kundennummer
        self.name_feld.setzen(kunde.name)
        self.strasse_feld.setzen(kunde.strasse)
        self.plz_feld.setzen(kunde.plz_text)
        self.ort_feld.setzen(kunde.ort)
        self.sticker_label.configure(
            text=f"{kunde.sticker_kontostand} / {len(sticker_modell.MOTIVE)}"
        )
        self.album.zeigen(self.anwendung.kunden_service.sticker_album(kundennummer))
        self.starterset_info.configure(text=self._starterset_text(kundennummer))

        if kunde.newsletter_aktiv:
            self.newsletter_haken.select()
        else:
            self.newsletter_haken.deselect()

        self.gutschein_info.configure(
            text=(
                "Gutschein offen – wird beim nächsten Kauf angeboten."
                if kunde.darf_newsletter_rabatt_nutzen
                else "Kein offener Gutschein."
            )
        )

    def _maske_leeren(self) -> None:
        self.gewaehlte_kundennummer = None
        self.name_feld.leeren()
        self.strasse_feld.leeren()
        self.plz_feld.leeren()
        self.ort_feld.leeren()
        self.newsletter_haken.deselect()
        self.sticker_label.configure(text=f"0 / {len(sticker_modell.MOTIVE)}")
        self.album.zeigen({})
        self.starterset_info.configure(text="")
        self.gutschein_info.configure(text="")

    def _starterset_text(self, kundennummer: int) -> str:
        """Wo der Kunde beim Starterset-Sonderangebot steht (/F53/)."""
        stand = self.anwendung.kunden_service.starterset_stand(kundennummer)

        if stand.erhalten:
            return f"{starterset_modell.TITEL} erhalten: {starterset_modell.inhalt_text()}."
        if stand.anspruch_offen:
            return (
                f"{starterset_modell.TITEL} steht zu — wird beim nächsten Kauf "
                f"ausgegeben."
            )

        fehlend = stand.fehlende_bestellungen
        if fehlend:
            einkaeufe = "Einkauf" if fehlend == 1 else "Einkäufe"
            return (
                f"{starterset_modell.TITEL} ({starterset_modell.inhalt_text()}): "
                f"noch {fehlend} {einkaeufe} bis zur vollen Sammlung."
            )
        return (
            f"{starterset_modell.TITEL} ({starterset_modell.inhalt_text()}): "
            f"Sammlung noch nicht vollständig."
        )

    # ------------------------------------------------------------------
    # Aktionen
    # ------------------------------------------------------------------

    def _anlegen(self) -> None:
        """/F42/ Neuen Kunden anlegen."""
        try:
            kunde = self.anwendung.kunden_service.anlegen(
                name=self.name_feld.wert(),
                strasse=self.strasse_feld.wert(),
                plz=ganzzahl_aus_text(self.plz_feld.wert() or "0", "PLZ"),
                ort=self.ort_feld.wert(),
                newsletter=bool(self.newsletter_haken.get()),
            )
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.gewaehlte_kundennummer = kunde.kundennummer
        self._liste_laden()
        self.hinweis_anzeigen(
            "Kunde angelegt",
            f"{kunde.name} hat die Kundennummer {kunde.kundennummer}."
            + (
                "\n\nDer Newsletter-Willkommensrabatt steht ab sofort bereit."
                if kunde.darf_newsletter_rabatt_nutzen
                else ""
            ),
        )

    def _speichern(self) -> None:
        if self.gewaehlte_kundennummer is None:
            self.melden(
                "Kein Kunde gewählt – bitte links anklicken oder neu anlegen.", art="fehler"
            )
            return
        try:
            kunde = self.anwendung.kunden_service.laden(self.gewaehlte_kundennummer)
            kunde.name = self.name_feld.wert()
            kunde.strasse = self.strasse_feld.wert()
            kunde.plz = ganzzahl_aus_text(self.plz_feld.wert() or "0", "PLZ")
            kunde.ort = self.ort_feld.wert()
            self.anwendung.kunden_service.aktualisieren(kunde)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self._liste_laden()
        self.melden(f"Daten von {kunde.name} gespeichert.")

    def _newsletter_umgeschaltet(self) -> None:
        """/F52/ An- oder Abmeldung zum Newsletter."""
        if self.gewaehlte_kundennummer is None:
            # Bei einem neuen Kunden entscheidet der Haken erst beim Anlegen.
            return
        try:
            kunde = self.anwendung.kunden_service.newsletter_umschalten(
                self.gewaehlte_kundennummer, bool(self.newsletter_haken.get())
            )
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self.gutschein_info.configure(
            text=(
                "Gutschein offen – wird beim nächsten Kauf angeboten."
                if kunde.darf_newsletter_rabatt_nutzen
                else "Kein offener Gutschein."
            )
        )
        self._liste_laden()

    def _loeschen(self) -> None:
        """/F43/ Kunden löschen, Bestellungen anonymisieren."""
        if self.gewaehlte_kundennummer is None:
            return
        try:
            kunde = self.anwendung.kunden_service.laden(self.gewaehlte_kundennummer)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        if not self.frage_stellen(
            "Kunde löschen?",
            f"{kunde.name} wird aus der Kartei entfernt. Die Bestellungen bleiben "
            "erhalten, sind danach aber keinem Kunden mehr zugeordnet.",
            ja_text="Löschen",
        ):
            return

        try:
            self.anwendung.kunden_service.loeschen(kunde.kundennummer)
        except FanshopFehler as fehler:
            self.fehler_anzeigen(fehler)
            return

        self._maske_leeren()
        self._liste_laden()
