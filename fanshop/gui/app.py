"""Das Hauptfenster des WI Fanshop.

Aufbau (siehe DESIGN.md, Abschnitt Layout):

    +----------------+--------------------------------------------+
    | Navigation     |  Arbeitsbereich                            |
    | 232 px         |  Karten auf abgetoenter Seite              |
    +----------------+--------------------------------------------+

Die Navigationsleiste ist die einzige Konstante der Oberflaeche. Sie traegt
oben das Logo der htw saar - im Hellmodus die allgemeine schwarze Wortmarke mit
dem Vierfarbbalken, im Dunkelmodus das goldene Logo der Fakultaet fuer
Wirtschaftswissenschaften.
"""

import customtkinter as ctk

from fanshop.gui import bausteine, design
from fanshop.gui.design import ABSTAND, RADIUS, farbe, schrift
from fanshop.gui.seite_artikel import ArtikelSeite
from fanshop.gui.seite_berichte import BerichteSeite
from fanshop.gui.seite_kasse import KassenSeite
from fanshop.gui.seite_kunden import KundenSeite
from fanshop.gui.seite_retouren import RetourenSeite

# Reihenfolge = Arbeitsablauf. Die Kasse steht oben, weil sie in den
# allermeisten Faellen gemeint ist.
#: Symbole fuer den Hell-/Dunkel-Schalter (/F54/).
SONNE = "☀"     # ☀
MOND = "☽"      # ☽ zunehmender Mond

EINTRAEGE = [
    ("kasse", "Kasse"),
    ("artikel", "Sortiment"),
    ("kunden", "Kunden"),
    ("retouren", "Retouren"),
    ("berichte", "Berichte"),
]


class FanshopApp(ctk.CTk):
    """Das Hauptfenster: Navigation links, wechselnde Seite rechts."""

    def __init__(self, anwendung) -> None:
        super().__init__()
        self.anwendung = anwendung

        self.title("WI Fanshop – Kassensystem und Warenwirtschaft | htw saar")
        self.geometry(f"{design.FENSTER_MINDESTBREITE}x{design.FENSTER_MINDESTHOEHE}")
        self.minsize(design.FENSTER_MINDESTBREITE, design.FENSTER_MINDESTHOEHE)
        self.configure(fg_color=farbe("papier"))

        # Spalte 1 (der Arbeitsbereich) darf wachsen, die Navigation nicht.
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.seiten: dict[str, object] = {}
        self.navigationsknoepfe: dict[str, ctk.CTkButton] = {}
        self.aktive_seite = ""

        self._navigation_bauen()
        self._seiten_bauen()

        self.seite_zeigen("kasse")
        self.protocol("WM_DELETE_WINDOW", self._beenden)

    # -- Navigationsleiste -------------------------------------------------

    def _navigation_bauen(self) -> None:
        self.navigation = ctk.CTkFrame(
            self,
            width=design.NAVIGATIONSBREITE,
            corner_radius=RADIUS["kante"],
            fg_color=farbe("leiste"),
        )
        self.navigation.grid(row=0, column=0, sticky="nsew")
        self.navigation.grid_propagate(False)

        # Im Hellmodus trennt eine Haarlinie die Leiste von der Seite; im
        # Dunkelmodus macht das der Helligkeitsunterschied allein.
        self.trennlinie = ctk.CTkFrame(
            self, width=1, fg_color=farbe("linie"), corner_radius=0
        )
        self.trennlinie.grid(row=0, column=0, sticky="nse")

        # -- Kopf: Logo und Vierfarbbalken -----------------------------
        self.logobereich = ctk.CTkFrame(self.navigation, fg_color="transparent")
        self.logobereich.pack(
            fill="x", padx=ABSTAND["md"], pady=(ABSTAND["lg"], ABSTAND["md"])
        )
        self.logo_label = ctk.CTkLabel(self.logobereich, text="")
        self.logo_label.pack(anchor="w")

        self.balken = bausteine.HtwBalken(self.logobereich, hoehe=4)
        self.balken.pack(fill="x", pady=(ABSTAND["sm"], 0))

        ctk.CTkLabel(
            self.logobereich,
            text="WI FANSHOP",
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", pady=(ABSTAND["sm"], 0))

        self._logo_aktualisieren()

        # -- Menuepunkte ------------------------------------------------
        for schluessel, beschriftung in EINTRAEGE:
            knopf = ctk.CTkButton(
                self.navigation,
                text=beschriftung,
                font=schrift("knopf"),
                anchor="w",
                height=42,
                corner_radius=RADIUS["bedienung"],
                border_width=0,
                command=lambda s=schluessel: self.seite_zeigen(s),
            )
            # Der Innenabstand links macht aus dem Klotz eine Liste.
            knopf.pack(fill="x", padx=ABSTAND["md"], pady=(0, 2))
            self.navigationsknoepfe[schluessel] = knopf

        # -- Fuss: Hell/Dunkel (/F54/) ----------------------------------
        fussbereich = ctk.CTkFrame(self.navigation, fg_color="transparent")
        fussbereich.pack(side="bottom", fill="x", padx=ABSTAND["md"], pady=ABSTAND["md"])

        # Sonne und Mond statt "Hell"/"Dunkel": Das Symbolpaar ist ueberall
        # dasselbe und braucht keine Ueberschrift darueber.
        self.modus_schalter = ctk.CTkSegmentedButton(
            fussbereich,
            values=[SONNE, MOND],
            font=schrift("symbol"),
            height=38,
            command=self._modus_gewaehlt,
        )
        self.modus_schalter.set(SONNE)
        self.modus_schalter.pack(fill="x")

    def _logo_aktualisieren(self) -> None:
        """Lädt das zum Modus passende htw-saar-Logo."""
        pfad, umfaerben = design.logo_datei()
        # Im Hellmodus ist es die reine Wortmarke - die darf die Leiste fast
        # ausfuellen. Das Fakultaetslogo im Dunkelmodus ist dreizeilig und
        # braucht dieselbe Breite fuer weniger Hoehe.
        logo = bausteine.logo_laden(pfad, breite=196, fuer_dunklen_grund=umfaerben)

        if logo is not None:
            self._logo_referenz = logo
            self.logo_label.configure(image=logo, text="")
        else:
            self.logo_label.configure(
                image=None,
                text="htw saar",
                font=schrift("titel_gross"),
                text_color=farbe("text"),
            )

        # Der Vierfarbbalken gehört zur allgemeinen Wortmarke im Hellmodus.
        # Im Dunkelmodus trägt das Fakultätslogo die Farbe schon selbst.
        if design.aktueller_index() == 0:
            self.balken.pack(fill="x", pady=(ABSTAND["sm"], 0))
        else:
            self.balken.pack_forget()

    # -- Seiten ------------------------------------------------------------

    def _seiten_bauen(self) -> None:
        """Legt alle fünf Seiten einmal an.

        Sie bleiben im Speicher und werden nur ein- und ausgeblendet. Dadurch
        bleiben Suchtext, Filter und Auswahl erhalten, wenn man kurz auf eine
        andere Seite wechselt.
        """
        self.seitenbereich = ctk.CTkFrame(self, fg_color="transparent")
        self.seitenbereich.grid(
            row=0, column=1, sticky="nsew", padx=ABSTAND["xl"], pady=ABSTAND["lg"]
        )

        seitenklassen = {
            "kasse": KassenSeite,
            "artikel": ArtikelSeite,
            "kunden": KundenSeite,
            "retouren": RetourenSeite,
            "berichte": BerichteSeite,
        }
        for schluessel, klasse in seitenklassen.items():
            self.seiten[schluessel] = klasse(self.seitenbereich, self.anwendung)

    def seite_zeigen(self, schluessel: str) -> None:
        """Blendet eine Seite ein und alle anderen aus."""
        for name, seite in self.seiten.items():
            if name == schluessel:
                seite.pack(fill="both", expand=True)
            else:
                seite.pack_forget()

        self._navigation_einfaerben(schluessel)
        self.aktive_seite = schluessel
        self.seiten[schluessel].beim_anzeigen()

    def _navigation_einfaerben(self, schluessel: str) -> None:
        """Der aktive Eintrag ist die einzige Goldfläche der Navigation."""
        for name, knopf in self.navigationsknoepfe.items():
            if name == schluessel:
                knopf.configure(
                    fg_color=farbe("akzent"),
                    hover_color=farbe("akzent"),
                    text_color=farbe("schwarz"),
                )
            else:
                knopf.configure(
                    fg_color="transparent",
                    hover_color=farbe("karton_tief"),
                    text_color=farbe("text"),
                )

    # -- /F54/ Hell- und Dunkelmodus ---------------------------------------

    def _modus_gewaehlt(self, auswahl: str) -> None:
        ctk.set_appearance_mode("dark" if auswahl == MOND else "light")

        # Logo und Trennlinie hängen am Modus, die Tabellen färben sich als
        # Tkinter-Widgets nicht selbst um.
        self._logo_aktualisieren()
        self._navigation_einfaerben(self.aktive_seite)
        self.trennlinie.configure(fg_color=farbe("linie"))
        for seite in self.seiten.values():
            seite.stil_aktualisieren()

    # -- Beenden -----------------------------------------------------------

    def _beenden(self) -> None:
        self.anwendung.schliessen()
        self.destroy()
