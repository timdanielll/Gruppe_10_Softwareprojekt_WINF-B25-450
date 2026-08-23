"""Designsystem des WI Fanshop als Python-Konstanten.

**Quelle der Wahrheit ist die Datei DESIGN.md im Projektwurzelverzeichnis.**
Dieses Modul ist nur die Uebersetzung derselben Werte nach Python, damit der
GUI-Code sie benutzen kann. Wer eine Farbe aendern will, aendert zuerst
DESIGN.md und zieht sie danach hier und in htw_saar_theme.json nach.

Grundregeln aus DESIGN.md, die man beim GUI-Bauen im Kopf haben muss:

* ``akzent`` markiert ausschliesslich die eine Aktion pro Bildschirm, die Geld
  oder Lagerbestand veraendert - und den aktiven Navigationseintrag. Im
  Hellmodus ist das htw-Blau, im Dunkelmodus WiWi-Gold.
* ``akzent`` ist niemals Schriftfarbe. Fuer Rabatttexte gibt es ``rabatt``.
* Jede Geldsumme und jede Nummer wird in einer ``zahl``-Schriftrolle gesetzt
  und rechtsbuendig ausgerichtet.
* Radius sagt, was ein Element ist: 0 = randlose Flaeche, 6 = Bedienelement,
  8 = Karte, 12 = Dialog.
* Keine Schatten. Trennung durch Abstand, sonst durch eine 1-px-Haarlinie.
"""

import platform
import tkinter.font

import customtkinter as ctk

from fanshop import konfiguration

# ---------------------------------------------------------------------------
# Farben - je Eintrag (Hellmodus, Dunkelmodus)
# ---------------------------------------------------------------------------
# CustomTkinter erwartet Farben als Liste [hell, dunkel] und schaltet selbst um.

FARBEN: dict[str, tuple[str, str]] = {
    # -- Flaechen: die Karte liegt heller auf der Seite -------------------
    # Das ist der Tiefeneindruck ohne Schatten. Im Hellmodus ist die Seite
    # leicht abgetoent und die Karte fast weiss, im Dunkelmodus umgekehrt.
    "papier":       ("#F3F1ED", "#171512"),   # Seitenhintergrund
    "karton":       ("#FCFBF8", "#221F1A"),   # Karten, Panels, Tabellenzeilen
    "karton_tief":  ("#EFEDE7", "#2B2721"),   # Tabellenkopf, gefuellte Zonen
    "leiste":       ("#FCFBF8", "#121110"),   # Navigationsleiste
    "feld":         ("#FFFFFF", "#0E0D0C"),   # Eingabefelder (die Vertiefung)
    "schwarz":      ("#161616", "#161616"),   # Wortmarken-Schwarz, feststehend
    # -- Schrift ---------------------------------------------------------
    "text":         ("#1C1A17", "#EDE9E1"),   # Fliesstext
    "text_leise":   ("#6A6459", "#A79E90"),   # Spaltenkoepfe, Hilfetexte
    "text_invers":  ("#FBFAF8", "#EDE9E1"),   # Schrift auf dunkler Flaeche
    # -- Signale ---------------------------------------------------------
    # Je Modus ein eigener Akzent - genau wie beim Logo:
    # Hell zeigt die allgemeine htw saar (Institutsblau aus dem Vierfarbbalken),
    # Dunkel die Fakultaet fuer Wirtschaftswissenschaften (WiWi-Gold).
    # Beide tragen schwarze Schrift und erfuellen WCAG AA.
    "akzent":       ("#4CC2EE", "#F7A823"),   # nur als Flaeche, nie als Schrift
    "akzent_hover": ("#26B5EA", "#D98D0B"),
    "akzent_weich": ("#D6EFFA", "#3A2E12"),   # stark aufgehellt: Auswahl, Hover
    "rabatt":       ("#8A5A05", "#F7A823"),   # Gold als Schrift (abgedunkelt)
    "fehler":       ("#B23A17", "#E8845F"),
    "erfolg":       ("#5C6B14", "#AFCB34"),
    # -- Linien ----------------------------------------------------------
    "linie":        ("#E2DED6", "#34302A"),
    # -- Vierfarbbalken der htw saar (aus assets/favicon.png) ------------
    # Die Hochschule fuehrt diese vier Farben als gemeinsame Klammer ueber
    # alle Fakultaeten. Sie erscheinen ausschliesslich als schmaler Balken
    # unter der Wortmarke - nie als Flaeche und nie als Schriftfarbe.
    "htw_gruen":    ("#AFCB05", "#AFCB05"),
    "htw_blau":     ("#00A8E7", "#00A8E7"),
    "htw_magenta":  ("#E82C8A", "#E82C8A"),
    "htw_orange":   ("#F7A600", "#F7A600"),
}

#: Reihenfolge des Vierfarbbalkens, wie ihn die htw saar verwendet.
HTW_BALKEN = ("htw_gruen", "htw_blau", "htw_magenta", "htw_orange")


def farbe(name: str) -> list[str]:
    """Liefert eine Farbe als ``[hell, dunkel]`` fuer CustomTkinter.

    Beispiel::

        ctk.CTkLabel(self, text="Hallo", text_color=farbe("text_leise"))
    """
    hell, dunkel = FARBEN[name]
    return [hell, dunkel]


# ---------------------------------------------------------------------------
# Abstaende und Radien (4-px-Basis)
# ---------------------------------------------------------------------------

ABSTAND = {
    "xs": 4,    # innerhalb eines Chips
    "sm": 8,    # zwischen zusammengehoerigen Steuerelementen
    "md": 16,   # zwischen Steuerelement-Gruppen
    "lg": 24,   # Innenabstand von Panels
    "xl": 40,   # Seitenrand
}

RADIUS = {
    "kante": 0,        # Tabellen und Navigationsleiste bleiben rechteckig
    "bedienung": 6,    # Buttons, Eingabefelder, Chips
    "karte": 8,        # Panels und Karten
    "dialog": 12,      # nur das modale Fenster
}

# Feste Masse aus DESIGN.md (Abschnitt Layout)
NAVIGATIONSBREITE = 232
ZEILENHOEHE = 30
FENSTER_MINDESTBREITE = 1280
FENSTER_MINDESTHOEHE = 800

#: Kantenlaenge der Produktfotos in der Artikelkarte.
BILDGROESSE = 104

# ---------------------------------------------------------------------------
# Schriften
# ---------------------------------------------------------------------------
# Die Hausschrift der htw saar (Akkurat) ist kommerziell lizenziert und darf
# nicht mitgeliefert werden. Wir benutzen deshalb je Betriebssystem die
# naechstliegende vorhandene Grotesk - und eine Dickengleiche fuer Zahlen.

_GROTESK_KETTE = {
    "Windows": ["Segoe UI", "Tahoma", "Arial"],
    "Darwin": ["Helvetica Neue", "Helvetica", "Arial"],
    "Linux": ["DejaVu Sans", "Liberation Sans", "FreeSans"],
}
_ZAHL_KETTE = {
    "Windows": ["Consolas", "Courier New"],
    "Darwin": ["Menlo", "Monaco", "Courier New"],
    "Linux": ["DejaVu Sans Mono", "Liberation Mono", "FreeMono"],
}

# Rolle -> (Schriftfamilie, Groesse in px, Schnitt)
# Es gibt bewusst nur zwei Schnitte: "normal" (400) und "bold" (700).
SCHRIFTROLLEN: dict[str, tuple[str, int, str]] = {
    "display":     ("grotesk", 28, "bold"),      # Seitentitel
    "titel_gross": ("grotesk", 20, "bold"),      # Panel-Ueberschrift
    "titel":       ("grotesk", 17, "bold"),      # Dialogtitel
    "text":        ("grotesk", 14, "normal"),    # Fliesstext, Tabellenzellen
    "text_klein":  ("grotesk", 12, "normal"),    # Hilfetexte
    "label":       ("grotesk", 11, "bold"),      # VERSALLABELS ueber Feldern
    "knopf":       ("grotesk", 13, "bold"),      # Beschriftung von Schaltflaechen
    "symbol":      ("grotesk", 18, "normal"),    # Sonne/Mond im Ansichtsschalter
    "zahl_gross":  ("zahl",    22, "bold"),      # Endbetrag
    "zahl":        ("zahl",    14, "normal"),    # Geldspalten
    "zahl_klein":  ("zahl",    12, "normal"),    # Kunden- und Artikelnummern
}

# Merkt sich bereits erzeugte Schriften, damit nicht bei jedem Aufruf ein
# neues Font-Objekt entsteht.
_schriften_zwischenspeicher: dict[str, ctk.CTkFont] = {}
_familien_zwischenspeicher: dict[str, str] = {}


def _erste_vorhandene_familie(kandidaten: list[str], ersatz: str) -> str:
    """Sucht die erste auf diesem Rechner installierte Schriftfamilie."""
    try:
        vorhanden = {name.lower() for name in tkinter.font.families()}
    except RuntimeError:
        # Es gibt noch kein Tk-Fenster - dann nehmen wir den ersten Kandidaten.
        return kandidaten[0]
    for kandidat in kandidaten:
        if kandidat.lower() in vorhanden:
            return kandidat
    return ersatz


def schriftfamilie(art: str) -> str:
    """Liefert 'grotesk' oder 'zahl' als konkreten Schriftnamen."""
    if art in _familien_zwischenspeicher:
        return _familien_zwischenspeicher[art]

    system = platform.system()
    ketten = _GROTESK_KETTE if art == "grotesk" else _ZAHL_KETTE
    kandidaten = ketten.get(system, ketten["Linux"])
    ersatz = "TkDefaultFont" if art == "grotesk" else "TkFixedFont"

    name = _erste_vorhandene_familie(kandidaten, ersatz)
    _familien_zwischenspeicher[art] = name
    return name


def schrift(rolle: str) -> ctk.CTkFont:
    """Liefert die Schrift zu einer Rolle aus ``SCHRIFTROLLEN``.

    Beispiel::

        ctk.CTkLabel(self, text="Gesamtbetrag", font=schrift("zahl_gross"))

    Wichtig: Diese Funktion darf erst aufgerufen werden, wenn das Hauptfenster
    existiert - CustomTkinter braucht dafuer ein laufendes Tk.
    """
    if rolle in _schriften_zwischenspeicher:
        return _schriften_zwischenspeicher[rolle]

    art, groesse, schnitt = SCHRIFTROLLEN[rolle]
    neue_schrift = ctk.CTkFont(family=schriftfamilie(art), size=groesse, weight=schnitt)
    _schriften_zwischenspeicher[rolle] = neue_schrift
    return neue_schrift


# ---------------------------------------------------------------------------
# Aktivierung des Designs
# ---------------------------------------------------------------------------

# Die Theme-Datei enthaelt dieselben Werte wie FARBEN, nur in dem Format, das
# CustomTkinter selbst versteht. Sie darf **keine** Kommentarschluessel
# enthalten - CustomTkinter erwartet unter jedem Schluessel ein Woerterbuch.
THEME_DATEI = konfiguration.PROJEKT_VERZEICHNIS / "fanshop" / "gui" / "htw_saar_theme.json"


def design_aktivieren(modus: str = "light") -> None:
    """Laedt das htw-saar-Design. Muss VOR dem Erzeugen des Fensters laufen.

    :param modus: "light" oder "dark" (/F54/).
    """
    ctk.set_default_color_theme(str(THEME_DATEI))
    ctk.set_appearance_mode(modus)


def modus_umschalten() -> str:
    """Schaltet zwischen Hell- und Dunkelmodus um und gibt den neuen Modus zurueck."""
    neuer_modus = "dark" if ctk.get_appearance_mode() == "Light" else "light"
    ctk.set_appearance_mode(neuer_modus)
    return neuer_modus


def aktueller_index() -> int:
    """0 im Hellmodus, 1 im Dunkelmodus.

    Wird gebraucht, wo Tkinter-Widgets (z. B. die Tabelle) nur eine einzelne
    Farbe akzeptieren und nicht das Paar [hell, dunkel].
    """
    return 1 if ctk.get_appearance_mode() == "Dark" else 0


def einzelfarbe(name: str) -> str:
    """Liefert genau die Farbe des aktuell aktiven Modus als '#RRGGBB'."""
    return FARBEN[name][aktueller_index()]


def logo_datei() -> tuple:
    """Welches htw-saar-Logo passt zum aktuellen Modus?

    :return: (Pfad, muss_umgefaerbt_werden)

    Die Hochschule liefert zwei Logovarianten, und beide werden hier benutzt:

    * **Hellmodus** - die reine Wortmarke ``htwsaar_Logo_LA.png``. Bewusst
      **nicht** die Kompaktvariante: Die traegt rechts daneben noch
      "Hochschule fuer Technik und Wirtschaft des Saarlandes" in winziger
      Schrift. In einer 232 Pixel breiten Leiste ist das unleserlich und
      stiehlt der Wortmarke den Platz. Darunter zeichnet die Anwendung den
      Vierfarbbalken der Hochschule.
    * **Dunkelmodus** - das Fakultaetslogo ``htwsaar_Logo_wiwi.png``.
      Seine goldene Zeile leuchtet auf dunklem Grund; nur die schwarze
      Wortmarke darunter muss auf Papierweiss umgefaerbt werden.
    """
    if aktueller_index() == 1:
        return konfiguration.ASSETS_VERZEICHNIS / "htwsaar_Logo_wiwi.png", True
    return konfiguration.ASSETS_VERZEICHNIS / "htwsaar_Logo_LA.png", False
