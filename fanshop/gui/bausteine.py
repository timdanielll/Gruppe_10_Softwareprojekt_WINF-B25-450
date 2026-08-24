"""Wiederverwendbare GUI-Bausteine.

Alle Seiten benutzen dieselben Bausteine, damit die Oberflaeche ueberall gleich
aussieht und niemand dieselbe Tabelle fuenfmal neu baut:

* :class:`Ueberschrift`   - Seitentitel
* :class:`Panel`          - Karte mit optionaler Titelzeile
* :class:`HtwBalken`      - der Vierfarbbalken der htw saar
* :class:`Feld`           - Beschriftung plus Eingabefeld (mit Fehlerzeile)
* :class:`Tabelle`        - Liste mit Kopfzeile, Auswahl und Leerzustand
* :class:`Bildkarte`      - Produktfoto mit Titel, Preis und Bestand
* :class:`Kachel`         - grosse Kennzahl fuer die Berichte
* :class:`Schrittleiste`  - die Strecke durch den Kassiervorgang
* :class:`Statuszeile`    - Rueckmeldung nach jedem Klick
* :class:`Dialog`         - modales Fenster fuer Meldungen und Rueckfragen
* :func:`aktionsknopf`    - der eine goldene Button pro Bildschirm

Die Regeln, nach denen hier gestaltet wird, stehen in ``DESIGN.md``.
"""

from pathlib import Path
from tkinter import ttk

import customtkinter as ctk

from fanshop.gui import design
from fanshop.gui.design import ABSTAND, RADIUS, farbe, schrift


# ---------------------------------------------------------------------------
# Text und Flaechen
# ---------------------------------------------------------------------------

class Ueberschrift(ctk.CTkLabel):
    """Der Titel einer Seite - das groesste Textelement oben links."""

    def __init__(self, master, text: str, **kwargs) -> None:
        """Baut eine Bereichsueberschrift."""
        super().__init__(
            master,
            text=text,
            font=schrift("display"),
            text_color=farbe("text"),
            anchor="w",
            **kwargs,
        )


class Panel(ctk.CTkFrame):
    """Eine Karte: hellere Flaeche, die auf der Seite liegt.

    Der Inhalt kommt in ``panel.inhalt`` - nicht direkt in das Panel, sonst
    liegt er neben der Titelzeile.
    """

    def __init__(self, master, titel: str = "", **kwargs) -> None:
        """Baut eine Karte mit optionalem Titel und Inhaltsflaeche."""
        super().__init__(
            master,
            fg_color=farbe("karton"),
            corner_radius=RADIUS["karte"],
            **kwargs,
        )

        if titel:
            ctk.CTkLabel(
                self,
                text=titel,
                font=schrift("titel"),
                text_color=farbe("text"),
                anchor="w",
            ).pack(fill="x", padx=ABSTAND["lg"], pady=(ABSTAND["md"], 0))

        self.inhalt = ctk.CTkFrame(self, fg_color="transparent")
        self.inhalt.pack(
            fill="both",
            expand=True,
            padx=ABSTAND["lg"],
            pady=(ABSTAND["sm"] if titel else ABSTAND["md"], ABSTAND["md"]),
        )


class Haarlinie(ctk.CTkFrame):
    """Eine 1 Pixel hohe Trennlinie. Ersetzt in diesem Design jeden Schatten."""

    def __init__(self, master, **kwargs) -> None:
        """Baut eine duenne Trennlinie."""
        super().__init__(
            master, height=1, fg_color=farbe("linie"), corner_radius=0, **kwargs
        )


class HtwBalken(ctk.CTkFrame):
    """Der Vierfarbbalken der htw saar: grün, blau, magenta, orange.

    Die Hochschule führt diese vier Farben als gemeinsame Klammer über alle
    Fakultäten (siehe ``assets/favicon.png``). Er erscheint ausschließlich hier
    — als schmaler Streifen unter der Wortmarke — und sonst nirgends in der
    Oberfläche.
    """

    def __init__(self, master, hoehe: int = 4, **kwargs) -> None:
        """Baut den Vierfarbbalken der htw saar."""
        super().__init__(master, fg_color="transparent", height=hoehe, width=1, **kwargs)
        for name in design.HTW_BALKEN:
            # width=1 ist wichtig: CustomTkinter-Rahmen fordern sonst je 200 px
            # an, und der Balken würde die ganze Navigationsleiste breitziehen.
            ctk.CTkFrame(
                self, fg_color=farbe(name), corner_radius=0, height=hoehe, width=1
            ).pack(side="left", fill="both", expand=True)


class Hinweis(ctk.CTkLabel):
    """Leiser Hilfetext unter einem Feld oder neben einer Tabelle.

    :param umbruch: Breite in Pixeln, ab der umbrochen wird. 0 bedeutet
                    einzeilig - sinnvoll fuer kurze Hinweise neben Knoepfen.
    """

    def __init__(self, master, text: str = "", umbruch: int = 0, **kwargs) -> None:
        """Baut eine kleine, leise Hinweiszeile."""
        super().__init__(
            master,
            text=text,
            font=schrift("text_klein"),
            text_color=farbe("text_leise"),
            anchor="w",
            justify="left",
            wraplength=umbruch,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# Eingabe
# ---------------------------------------------------------------------------

class Feld(ctk.CTkFrame):
    """Beschriftung, Eingabefeld und Platz für eine Fehlermeldung.

    Jedes Feld hat eine **sichtbare Beschriftung**. Platzhaltertext ersetzt
    niemals eine Beschriftung - er verschwindet beim Tippen, und dann weiss
    niemand mehr, was in dem Feld steht.
    """

    def __init__(
        self,
        master,
        beschriftung: str,
        platzhalter: str = "",
        breite: int = 220,
        **kwargs,
    ) -> None:
        """Baut ein Eingabefeld mit Beschriftung und Fehlerzeile."""
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text=beschriftung.upper(),
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", pady=(0, 3))

        self.eingabe = ctk.CTkEntry(
            self,
            placeholder_text=platzhalter,
            width=breite,
            height=36,
            font=schrift("text"),
            corner_radius=RADIUS["bedienung"],
        )
        self.eingabe.pack(fill="x")

        self._fehlerzeile = ctk.CTkLabel(
            self,
            text="",
            font=schrift("text_klein"),
            text_color=farbe("fehler"),
            anchor="w",
        )

    # -- Werte -------------------------------------------------------------

    def wert(self) -> str:
        """Der eingetippte Text, ohne Leerzeichen am Rand."""
        return self.eingabe.get().strip()

    def setzen(self, text: str) -> None:
        """Schreibt einen Wert ins Feld."""
        self.eingabe.delete(0, "end")
        self.eingabe.insert(0, str(text))

    def leeren(self) -> None:
        """Loescht Inhalt und Fehlermeldung."""
        self.eingabe.delete(0, "end")
        self.fehler_loeschen()

    # -- Fehleranzeige (/NF11/) --------------------------------------------

    def fehler_zeigen(self, text: str) -> None:
        """Zeigt eine Meldung unter dem Feld - zusätzlich zum Dialogfenster.

        Der Dialog verschwindet nach dem Wegklicken, der Fehler bleibt.
        """
        self._fehlerzeile.configure(text=text)
        self._fehlerzeile.pack(fill="x", pady=(3, 0))
        self.eingabe.configure(border_color=design.einzelfarbe("fehler"))

    def fehler_loeschen(self) -> None:
        """Blendet die Fehlerzeile wieder aus."""
        self._fehlerzeile.pack_forget()
        self.eingabe.configure(border_color=design.einzelfarbe("linie"))


class Auswahlfeld(ctk.CTkFrame):
    """Beschriftung plus Auswahlliste (Dropdown)."""

    def __init__(
        self,
        master,
        beschriftung: str,
        werte: list[str],
        breite: int = 220,
        beim_waehlen=None,
        **kwargs,
    ) -> None:
        """Baut ein Dropdown mit Beschriftung."""
        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text=beschriftung.upper(),
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", pady=(0, 3))

        self.auswahl = ctk.CTkOptionMenu(
            self,
            values=werte or [""],
            width=breite,
            height=36,
            font=schrift("text"),
            corner_radius=RADIUS["bedienung"],
            command=beim_waehlen,
        )
        self.auswahl.pack(fill="x")

    def wert(self) -> str:
        """Der gerade gewaehlte Eintrag."""
        return self.auswahl.get()

    def setzen(self, text: str) -> None:
        """Waehlt einen Eintrag aus."""
        self.auswahl.set(text)

    def werte_setzen(self, werte: list[str]) -> None:
        """Tauscht die Auswahlliste aus und waehlt den ersten Eintrag."""
        self.auswahl.configure(values=werte or [""])
        if werte:
            self.auswahl.set(werte[0])


def aktionsknopf(master, text: str, befehl, breite: int = 200) -> ctk.CTkButton:
    """Der **eine** goldene Button pro Bildschirm.

    Er trägt die Aktion, die etwas Unwiderrufliches tut: Kauf abschließen,
    Retoure buchen, Artikel anlegen. Alles andere ist ein normaler Button.
    """
    return ctk.CTkButton(
        master,
        text=text,
        command=befehl,
        width=breite,
        height=44,
        font=schrift("knopf"),
        corner_radius=RADIUS["bedienung"],
        border_width=0,
        fg_color=farbe("akzent"),
        hover_color=farbe("akzent_hover"),
        text_color=farbe("schwarz"),
    )


def knopf(master, text: str, befehl, breite: int = 140) -> ctk.CTkButton:
    """Normaler (sekundärer) Button."""
    return ctk.CTkButton(
        master,
        text=text,
        command=befehl,
        width=breite,
        height=36,
        font=schrift("knopf"),
        corner_radius=RADIUS["bedienung"],
    )


def gefahrenknopf(master, text: str, befehl, breite: int = 140) -> ctk.CTkButton:
    """Button für Löschen und Deaktivieren - Stempelrot."""
    return ctk.CTkButton(
        master,
        text=text,
        command=befehl,
        width=breite,
        height=36,
        font=schrift("knopf"),
        corner_radius=RADIUS["bedienung"],
        border_width=0,
        fg_color=farbe("fehler"),
        hover_color=farbe("fehler"),
        text_color=farbe("text_invers"),
    )


# ---------------------------------------------------------------------------
# Bilder
# ---------------------------------------------------------------------------

#: Papierweiß als RGB-Tripel - gebraucht beim Umfärben der Logos.
FARBEN_PAPIER_RGB = (251, 250, 248)

#: Einmal geladene Bilder werden gemerkt. Ohne diesen Zwischenspeicher würde
#: jedes Auswählen eines Artikels die Datei erneut von der Platte lesen.
_bilder_zwischenspeicher: dict[tuple, object] = {}


def leeres_bild(breite: int, hoehe: int):
    """Ein vollständig durchsichtiges Bild in fester Größe.

    Wird gebraucht, um ein angezeigtes Foto wieder loszuwerden:
    ``configure(image=None)`` setzt zwar den Zustand des Widgets zurück,
    CustomTkinter zeichnet das alte Bild aber nicht weg — es bliebe sichtbar
    stehen. Ein durchsichtiges Bild derselben Größe überschreibt es sauber.
    """
    schluessel = ("__leer__", breite, hoehe, False)
    if schluessel in _bilder_zwischenspeicher:
        return _bilder_zwischenspeicher[schluessel]
    try:
        from PIL import Image

        leer = Image.new("RGBA", (breite, hoehe), (0, 0, 0, 0))
        fertig = ctk.CTkImage(light_image=leer, dark_image=leer, size=(breite, hoehe))
    except Exception:
        fertig = None
    _bilder_zwischenspeicher[schluessel] = fertig
    return fertig


def bild_laden(pfad: Path, breite: int, hoehe: int, blass: bool = False):
    """Lädt ein Bild in fester Größe. Fehlt die Datei, kommt None zurück.

    Ein fehlendes Produktfoto darf die Anwendung nie zum Absturz bringen.

    :param blass: True zeichnet das Bild grau und aufgehellt — so werden im
                  Sammelalbum die noch fehlenden Motive dargestellt.
    """
    schluessel = (str(pfad), breite, hoehe, blass)
    if schluessel in _bilder_zwischenspeicher:
        return _bilder_zwischenspeicher[schluessel]
    try:
        from PIL import Image

        bild = Image.open(pfad)
        if blass:
            bild = bild.convert("L").convert("RGB")
            weiss = Image.new("RGB", bild.size, (255, 255, 255))
            bild = Image.blend(bild, weiss, 0.55)
        fertig = ctk.CTkImage(light_image=bild, dark_image=bild, size=(breite, hoehe))
    except Exception:
        fertig = None
    _bilder_zwischenspeicher[schluessel] = fertig
    return fertig


class StickerAlbum(ctk.CTkFrame):
    """Das Sammelalbum eines Kunden (/F53/).

    Zeigt alle sechs Motive nebeneinander: die vorhandenen in Farbe, die
    fehlenden blass. Erst dadurch wird aus dem Zähler eine Sammlung — man
    sieht auf einen Blick, was noch fehlt.

    Unter jedem Motiv steht ein Haken oder ein Strich, keine Stückzahl: Jeder
    Sticker wird nur einmal vergeben, ein „2×" kann es also gar nicht geben.
    """

    def __init__(self, master, **kwargs) -> None:
        """Baut die Reihe fuer die sechs Sammelmotive."""
        super().__init__(master, fg_color="transparent", **kwargs)

        self.kopf = ctk.CTkLabel(
            self,
            text="SAMMLUNG",
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        )
        self.kopf.pack(fill="x", pady=(0, ABSTAND["xs"]))

        self.reihe = ctk.CTkFrame(self, fg_color="transparent")
        self.reihe.pack(fill="x")

        self._referenzen = []

    def zeigen(self, album: dict[str, int]) -> None:
        """Zeichnet das Album neu.

        :param album: Woerterbuch Motivschluessel -> Anzahl (immer 1)
        """
        from fanshop.modelle import sticker as sticker_modell

        for widget in self.reihe.winfo_children():
            widget.destroy()
        self._referenzen = []

        verschieden, gesamt = sticker_modell.album_fortschritt(album)
        self.kopf.configure(text=f"SAMMLUNG · {verschieden} VON {gesamt} MOTIVEN")

        for motiv in sticker_modell.MOTIVE:
            anzahl = album.get(motiv.schluessel, 0)
            spalte = ctk.CTkFrame(self.reihe, fg_color="transparent")
            spalte.pack(side="left", padx=(0, 3))

            # Sechs Motive nebeneinander muessen in die schmale Formularspalte
            # passen - deshalb bewusst klein.
            bild = bild_laden(motiv.pfad, 44, 33, blass=(anzahl == 0))
            if bild is not None:
                self._referenzen.append(bild)
                ctk.CTkLabel(spalte, image=bild, text="").pack()

            ctk.CTkLabel(
                spalte,
                text="✓" if anzahl else "–",
                font=schrift("zahl_klein"),
                text_color=farbe("text") if anzahl else farbe("text_leise"),
            ).pack()


def logo_laden(pfad: Path, breite: int, fuer_dunklen_grund: bool = False):
    """Lädt ein Logo und behält dabei das Seitenverhältnis.

    Das Fakultätslogo der htw saar trägt die Wortmarke „htw saar" in Schwarz.
    Auf dunklem Grund wäre sie unsichtbar, deshalb werden für diesen Fall alle
    dunklen Bildpunkte auf Papierweiß umgefärbt — die goldene Fakultätszeile
    bleibt unberührt.
    """
    schluessel = (str(pfad), breite, "hell" if not fuer_dunklen_grund else "dunkel")
    if schluessel in _bilder_zwischenspeicher:
        return _bilder_zwischenspeicher[schluessel]
    try:
        from PIL import Image

        bild = Image.open(pfad).convert("RGBA")

        if fuer_dunklen_grund:
            bildpunkte = bild.load()
            for x in range(bild.width):
                for y in range(bild.height):
                    r, g, b, a = bildpunkte[x, y]
                    # "dunkel" heisst: alle drei Kanaele niedrig -> die Wortmarke
                    if a > 0 and r < 100 and g < 100 and b < 100:
                        bildpunkte[x, y] = (*FARBEN_PAPIER_RGB, a)

        hoehe = max(1, round(breite * bild.height / bild.width))
        fertig = ctk.CTkImage(light_image=bild, dark_image=bild, size=(breite, hoehe))
    except Exception:
        fertig = None
    _bilder_zwischenspeicher[schluessel] = fertig
    return fertig


class Bildkarte(ctk.CTkFrame):
    """Zeigt einen Artikel mit Produktfoto, Titel, Preis und Bestand.

    Ersetzt die reine Zahlenzeile durch etwas, das der Bediener dem Kunden
    zudrehen kann. Ohne gewählten Artikel steht hier ein Hinweis statt einer
    leeren Fläche.
    """

    def __init__(self, master, **kwargs) -> None:
        """Baut die Karte fuer Produktfoto, Titel und Kennzahlen."""
        super().__init__(
            master, fg_color=farbe("karton_tief"), corner_radius=RADIUS["karte"], **kwargs
        )

        self.bildflaeche = ctk.CTkLabel(self, text="", width=design.BILDGROESSE)
        self.bildflaeche.pack(side="left", padx=ABSTAND["md"], pady=ABSTAND["md"])

        rechts = ctk.CTkFrame(self, fg_color="transparent")
        rechts.pack(side="left", fill="both", expand=True, pady=ABSTAND["md"],
                    padx=(0, ABSTAND["md"]))

        self.titel = ctk.CTkLabel(
            rechts, text="", font=schrift("titel"), text_color=farbe("text"),
            anchor="w", justify="left", wraplength=168,
        )
        self.titel.pack(fill="x")

        self.unterzeile = Hinweis(rechts, "", umbruch=168)
        self.unterzeile.pack(fill="x", pady=(2, 0))

        self.beschreibung = Hinweis(rechts, "", umbruch=168)
        self.beschreibung.pack(fill="x", pady=(ABSTAND["xs"], 0))

        zeile = ctk.CTkFrame(rechts, fg_color="transparent")
        zeile.pack(fill="x", pady=(ABSTAND["sm"], 0))

        self.preis = ctk.CTkLabel(
            zeile, text="", font=schrift("zahl_gross"), text_color=farbe("text"), anchor="w"
        )
        self.preis.pack(side="left")

        self.bestand = ctk.CTkLabel(
            zeile, text="", font=schrift("label"), text_color=farbe("erfolg"), anchor="e"
        )
        self.bestand.pack(side="right")

        self.leeren()

    def leeren(self, text: str = "Artikel in der Liste auswählen.") -> None:
        """Zeigt statt eines Fotos einen Platzhaltertext."""
        # Durchsichtiges Bild statt None - sonst bleibt das vorige Foto stehen.
        self._bild_referenz = leeres_bild(design.BILDGROESSE, design.BILDGROESSE)
        self.bildflaeche.configure(
            image=self._bild_referenz,
            text="kein\nFoto",
            font=schrift("text_klein"),
            text_color=farbe("text_leise"),
        )
        self.titel.configure(text=text)
        self.unterzeile.configure(text="")
        self.beschreibung.configure(text="")
        self.preis.configure(text="")
        self.bestand.configure(text="")

    def zeigen(self, artikel) -> None:
        """Füllt die Karte mit einem Artikel."""
        from fanshop import konfiguration
        from fanshop.hilfsmittel import euro, prozent

        bild = None
        if artikel.bildpfad:
            bild = bild_laden(
                konfiguration.ARTIKELBILDER_VERZEICHNIS / artikel.bildpfad,
                design.BILDGROESSE,
                design.BILDGROESSE,
            )
        # Ohne Foto wird ein durchsichtiges Bild gesetzt, damit ein vorher
        # gezeigtes Produktfoto wirklich verschwindet - CustomTkinter loescht
        # es bei image=None zwar aus dem Zustand, zeichnet es aber nicht weg.
        # Die Referenz verhindert ausserdem, dass Tkinter das Bild verwirft.
        self._bild_referenz = bild or leeres_bild(
            design.BILDGROESSE, design.BILDGROESSE
        )
        self.bildflaeche.configure(
            image=self._bild_referenz, text="" if bild else "kein\nFoto",
            font=schrift("text_klein"), text_color=farbe("text_leise"),
        )

        self.titel.configure(text=artikel.titel)

        teile = [artikel.kategorie]
        if artikel.merkmale():
            teile.append(artikel.merkmale())
        if artikel.hat_rabatt:
            teile.append(f"{prozent(artikel.rabattsatz)} Rabatt")
        self.unterzeile.configure(text="  ·  ".join(teile))

        beschreibung = artikel.beschreibung or ""
        if len(beschreibung) > 120:
            beschreibung = beschreibung[:117] + "…"
        self.beschreibung.configure(text=beschreibung)

        self.preis.configure(text=euro(artikel.endpreis))
        self.bestand.configure(
            text=f"{artikel.lagerbestand} auf Lager",
            text_color=farbe("erfolg") if artikel.lagerbestand > 3 else farbe("fehler"),
        )


class Kachel(ctk.CTkFrame):
    """Eine große Kennzahl mit Beschriftung - für die Berichtsseite."""

    def __init__(self, master, beschriftung: str, zusatz: str = "", **kwargs) -> None:
        """Baut eine Kennzahlkachel fuer die Berichte."""
        super().__init__(
            master, fg_color=farbe("karton"), corner_radius=RADIUS["karte"], **kwargs
        )

        ctk.CTkLabel(
            self,
            text=beschriftung.upper(),
            font=schrift("label"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", padx=ABSTAND["lg"], pady=(ABSTAND["md"], 0))

        self.wert = ctk.CTkLabel(
            self, text="–", font=schrift("zahl_gross"), text_color=farbe("text"), anchor="w"
        )
        self.wert.pack(fill="x", padx=ABSTAND["lg"], pady=(2, 0))

        ctk.CTkLabel(
            self,
            text=zusatz,
            font=schrift("text_klein"),
            text_color=farbe("text_leise"),
            anchor="w",
        ).pack(fill="x", padx=ABSTAND["lg"], pady=(0, ABSTAND["md"]))

    def setzen(self, text: str) -> None:
        """Schreibt eine neue Zahl in die Kachel."""
        self.wert.configure(text=text)


# ---------------------------------------------------------------------------
# Fuehrung durch einen Vorgang
# ---------------------------------------------------------------------------

class Schrittleiste(ctk.CTkFrame):
    """Die Strecke durch einen mehrstufigen Vorgang.

    Zeigt oben, wo man gerade steht: erledigte Schritte sind golden umrandet,
    der aktuelle ist golden gefüllt, spätere sind grau. Anklicken springt
    zurück — und vorwärts, sofern die Seite den Schritt freigibt.

    Damit erfüllt die Kasse /NF12/ sichtbar: „Der Kassiervorgang muss einem
    logischen, linearen Ablauf folgen."
    """

    def __init__(self, master, schritte: list[str], beim_springen=None, **kwargs) -> None:
        """Baut die Schrittanzeige der Kasse."""
        super().__init__(master, fg_color="transparent", **kwargs)

        self.schritte = schritte
        self.beim_springen = beim_springen
        self.aktueller = 0
        self._knoepfe: list[ctk.CTkButton] = []
        self._striche: list[ctk.CTkFrame] = []

        for nummer, beschriftung in enumerate(schritte):
            if nummer > 0:
                # width=1: sonst fordert jeder Strich 200 px an und der
                # letzte Schritt rutscht aus dem Fenster.
                strich = ctk.CTkFrame(
                    self, height=2, width=1, fg_color=farbe("linie"), corner_radius=0
                )
                strich.pack(side="left", fill="x", expand=True, padx=ABSTAND["xs"])
                self._striche.append(strich)

            knopf_widget = ctk.CTkButton(
                self,
                text=f"{nummer + 1}   {beschriftung}",
                font=schrift("knopf"),
                height=38,
                width=132,
                corner_radius=RADIUS["bedienung"],
                border_width=1,
                command=lambda n=nummer: self._angeklickt(n),
            )
            knopf_widget.pack(side="left")
            self._knoepfe.append(knopf_widget)

        self.setzen(0)

    def _angeklickt(self, nummer: int) -> None:
        """Meldet den Wunsch weiter - ob er erlaubt ist, entscheidet die Seite.

        Die Schrittleiste kennt die fachlichen Regeln nicht (etwa "der
        Warenkorb darf nicht leer sein"). Sie reicht den gewuenschten Schritt
        deshalb an die Seite durch, die dieselbe Pruefung benutzt wie der
        Knopf "Weiter".
        """
        if self.beim_springen:
            self.beim_springen(nummer)

    def setzen(self, aktueller: int) -> None:
        """Markiert den aktuellen Schritt und färbt die Strecke ein."""
        self.aktueller = aktueller
        for nummer, knopf_widget in enumerate(self._knoepfe):
            if nummer == aktueller:
                knopf_widget.configure(
                    fg_color=farbe("akzent"),
                    hover_color=farbe("akzent"),
                    text_color=farbe("schwarz"),
                    border_color=farbe("akzent"),
                )
            elif nummer < aktueller:
                knopf_widget.configure(
                    fg_color=farbe("akzent_weich"),
                    hover_color=farbe("akzent_weich"),
                    text_color=farbe("text"),
                    border_color=farbe("akzent"),
                )
            else:
                knopf_widget.configure(
                    fg_color="transparent",
                    hover_color=farbe("karton_tief"),
                    text_color=farbe("text_leise"),
                    border_color=farbe("linie"),
                )
        for nummer, strich in enumerate(self._striche):
            strich.configure(
                fg_color=farbe("akzent") if nummer < aktueller else farbe("linie")
            )


class Statuszeile(ctk.CTkFrame):
    """Rückmeldung nach jedem Klick.

    Ohne sie muss der Bediener raten, ob eine Aktion angekommen ist. Die
    Meldung bleibt einige Sekunden stehen und verblasst dann zum Ruhetext —
    kein Dialog, der weggeklickt werden muss.
    """

    RUHETEXT = "Bereit."

    def __init__(self, master, **kwargs) -> None:
        """Baut die Meldezeile am unteren Rand einer Seite."""
        super().__init__(master, fg_color="transparent", height=22, **kwargs)

        self.punkt = ctk.CTkLabel(
            self, text="●", font=schrift("text_klein"), text_color=farbe("text_leise"), width=12
        )
        self.punkt.pack(side="left")

        self.text = ctk.CTkLabel(
            self,
            text=self.RUHETEXT,
            font=schrift("text_klein"),
            text_color=farbe("text_leise"),
            anchor="w",
        )
        self.text.pack(side="left", padx=(ABSTAND["xs"], 0))

        self._auftrag = None

    def melden(self, nachricht: str, art: str = "erfolg", dauer: int = 4000) -> None:
        """Zeigt eine Rückmeldung.

        :param art: ``"erfolg"``, ``"fehler"`` oder ``"neutral"``
        :param dauer: Millisekunden bis zum Zurückfallen auf den Ruhetext
        """
        farbname = {"erfolg": "erfolg", "fehler": "fehler"}.get(art, "text_leise")
        self.punkt.configure(text_color=farbe(farbname))
        self.text.configure(text=nachricht, text_color=farbe(farbname))

        if self._auftrag is not None:
            self.after_cancel(self._auftrag)
        self._auftrag = self.after(dauer, self.zuruecksetzen)

    def zuruecksetzen(self) -> None:
        """Loescht die letzte Meldung."""
        self._auftrag = None
        self.punkt.configure(text_color=farbe("text_leise"))
        self.text.configure(text=self.RUHETEXT, text_color=farbe("text_leise"))


# ---------------------------------------------------------------------------
# Tabelle
# ---------------------------------------------------------------------------

class Tabelle(ctk.CTkFrame):
    """Eine Liste mit Kopfzeile, Bildlaufleiste und Leerzustand.

    Technisch steckt darin ein ``ttk.Treeview``, weil CustomTkinter selbst kein
    Tabellen-Widget mitbringt. Die Farben werden deshalb von Hand gesetzt und
    bei jedem Wechsel des Hell-/Dunkelmodus neu angewendet.

    Benutzung::

        tabelle = Tabelle(rahmen, spalten=[("Titel", 260, "w"), ("Preis", 90, "e")])
        tabelle.fuellen([(1, ["Tasse", "9,90 €"]), (2, ["Poster", "4,90 €"])])
        artikel_id = tabelle.gewaehlter_schluessel()
    """

    def __init__(
        self,
        master,
        spalten: list[tuple[str, int, str]],
        beim_waehlen=None,
        beim_doppelklick=None,
        leer_text: str = "Keine Einträge vorhanden.",
        hoehe: int = 10,
        **kwargs,
    ) -> None:
        """Baut eine Tabelle mit Spalten, Bildlauf und Zeilenmarkierung."""
        super().__init__(master, fg_color="transparent", **kwargs)

        self.spalten = spalten
        self.leer_text = leer_text

        namen = [f"spalte{nummer}" for nummer in range(len(spalten))]
        self.baum = ttk.Treeview(
            self,
            columns=namen,
            show="headings",
            height=hoehe,
            selectmode="browse",
            style="Fanshop.Treeview",
        )
        # Die Spaltenbreiten verwaltet diese Klasse selbst (siehe
        # _breiten_anpassen). ttk wuerde bei knappem Platz alle Spalten
        # gleichmaessig quetschen und die letzte einfach abschneiden.
        self._namen = namen
        self._breiteste = max(range(len(spalten)), key=lambda i: spalten[i][1])
        self._letzte_breite = 0

        for name, (ueberschrift, breite, ausrichtung) in zip(namen, spalten):
            self.baum.heading(name, text=ueberschrift.upper(), anchor=ausrichtung)
            self.baum.column(
                name, width=breite, minwidth=20, anchor=ausrichtung, stretch=False
            )

        # Bei jeder Groessenaenderung neu aufteilen - auch beim ersten Zeichnen.
        self.baum.bind("<Configure>", self._breiten_anpassen)

        self.leiste = ttk.Scrollbar(self, orient="vertical", command=self.baum.yview)
        self.baum.configure(yscrollcommand=self.leiste.set)

        self._kopfschrift = None

        self.baum.pack(side="left", fill="both", expand=True)
        self.leiste.pack(side="right", fill="y")

        # Leerzustand: liegt ueber der Tabelle und wird ein- und ausgeblendet.
        self.leer_hinweis = ctk.CTkLabel(
            self,
            text=leer_text,
            font=schrift("text"),
            text_color=farbe("text_leise"),
        )

        if beim_waehlen:
            self.baum.bind("<<TreeviewSelect>>", lambda ereignis: beim_waehlen())
        if beim_doppelklick:
            self.baum.bind("<Double-1>", lambda ereignis: beim_doppelklick())

        self.stil_anwenden()

    # -- Spaltenbreiten ----------------------------------------------------

    def _mindestbreite(self, ueberschrift: str) -> int:
        """Wie schmal darf eine Spalte werden, ohne ihre Überschrift zu kappen?

        Gemessen wird die tatsächliche Textbreite in der Kopfzeilenschrift,
        plus der Innenabstand aus ``stil_anwenden``. Raten führt hier zu genau
        dem Fehler, den die Methode verhindern soll.
        """
        import tkinter.font

        if self._kopfschrift is None:
            self._kopfschrift = tkinter.font.Font(
                family=design.schriftfamilie("grotesk"), size=9, weight="bold"
            )
        return self._kopfschrift.measure(ueberschrift.upper()) + 22

    def _breiten_anpassen(self, ereignis=None) -> None:
        """Verteilt die vorhandene Breite auf die Spalten.

        ``ttk`` kann das nicht von allein: Ist der Platz knapp, quetscht es
        alle Spalten gleichmäßig und schneidet die letzte einfach ab — es gibt
        keine waagerechte Bildlaufleiste. Deshalb rechnet die Tabelle bei jeder
        Größenänderung selbst:

        * **Genug Platz** → der Überschuss geht an die breiteste Spalte
          (in der Regel der Titel).
        * **Zu wenig Platz** → alle Spalten werden anteilig gekürzt, aber
          keine unter die Breite ihrer eigenen Überschrift.

        Dadurch bleibt jede Spalte sichtbar, egal wie groß das Fenster ist.
        """
        verfuegbar = self.baum.winfo_width()
        if verfuegbar <= 1 or verfuegbar == self._letzte_breite:
            return
        self._letzte_breite = verfuegbar

        minimum = [self._mindestbreite(ueberschrift) for ueberschrift, _, _ in self.spalten]
        # Die Wunschbreite ist nur ein Vorschlag - unter die Breite der eigenen
        # Ueberschrift darf keine Spalte, auch wenn im Code weniger steht.
        breiten = [
            max(breite, minimum[i]) for i, (_, breite, _) in enumerate(self.spalten)
        ]
        gesamt = sum(breiten)

        if verfuegbar >= gesamt:
            breiten[self._breiteste] += verfuegbar - gesamt
        else:
            # In mehreren Runden kuerzen: Spalten, die ihr Minimum erreicht
            # haben, fallen aus der Verteilung heraus.
            for _ in range(4):
                fehlend = sum(breiten) - verfuegbar
                if fehlend <= 0:
                    break
                kuerzbar = [max(0, breiten[i] - minimum[i]) for i in range(len(breiten))]
                summe = sum(kuerzbar)
                if summe <= 0:
                    break
                for i in range(len(breiten)):
                    if kuerzbar[i] > 0:
                        breiten[i] -= min(kuerzbar[i], round(fehlend * kuerzbar[i] / summe))

            # Letzte Stufe: Passt selbst die Summe der Mindestbreiten nicht
            # mehr (sehr kleines Fenster oder hohe Windows-Skalierung), werden
            # alle Spalten gleichmaessig gestaucht. Dann sind zwar ein paar
            # Ueberschriften gekuerzt - aber jede Spalte bleibt sichtbar.
            # Eine Spalte, die ganz aus dem Bild faellt, ist schlimmer.
            gestaucht = sum(breiten)
            if gestaucht > verfuegbar:
                faktor = verfuegbar / gestaucht
                breiten = [max(24, int(b * faktor)) for b in breiten]

        for name, breite in zip(self._namen, breiten):
            self.baum.column(name, width=max(20, breite))

    # -- Inhalt ------------------------------------------------------------

    def fuellen(
        self,
        zeilen: list[tuple],
        leer_text: str | None = None,
        markierungen: dict | None = None,
    ) -> None:
        """Füllt die Tabelle neu.

        :param zeilen: Liste aus ``(schluessel, [spaltenwerte...])``. Der
                       Schlüssel ist die Datensatz-ID und wird beim Auswählen
                       zurückgegeben.
        :param markierungen: optionale Zuordnung Schlüssel -> Markierung.
                             Erlaubt ist ``"erledigt"`` (graue, durchgestrichen
                             wirkende Zeile). Damit lässt sich ein Zustand
                             zeigen, statt ihn per Fehlermeldung zu erklären.
        """
        self.leeren()
        markierungen = markierungen or {}

        for schluessel, werte in zeilen:
            marke = markierungen.get(schluessel)
            self.baum.insert(
                "", "end", iid=str(schluessel), values=werte,
                tags=(marke,) if marke else (),
            )

        if zeilen:
            self.leer_hinweis.place_forget()
        else:
            self.leer_hinweis.configure(text=leer_text or self.leer_text)
            self.leer_hinweis.place(relx=0.5, rely=0.4, anchor="center")

    def leeren(self) -> None:
        """Entfernt alle Zeilen."""
        for eintrag in self.baum.get_children():
            self.baum.delete(eintrag)

    @property
    def ist_leer(self) -> bool:
        """True, wenn keine Zeile angezeigt wird."""
        return not self.baum.get_children()

    # -- Auswahl -----------------------------------------------------------

    def gewaehlter_schluessel(self) -> int | None:
        """Die ID der markierten Zeile - oder None, wenn nichts markiert ist."""
        auswahl = self.baum.selection()
        if not auswahl:
            return None
        try:
            return int(auswahl[0])
        except ValueError:
            return None

    def gewaehlter_schluessel_text(self) -> str | None:
        """Der Schluessel der markierten Zeile als Text - oder None.

        Wird gebraucht, wo eine Zeile nicht durch eine Zahl bestimmt ist: Im
        Warenkorb gehoert zur Kennung auch die Groesse (z. B. "12|L").
        """
        auswahl = self.baum.selection()
        return auswahl[0] if auswahl else None

    def auswahl_setzen(self, schluessel: int) -> None:
        """Markiert die Zeile mit diesem Schluessel."""
        eintrag = str(schluessel)
        if self.baum.exists(eintrag):
            self.baum.selection_set(eintrag)
            self.baum.see(eintrag)

    def erste_waehlen(self) -> None:
        """Markiert die erste Zeile - damit nie eine leere Detailkarte dasteht."""
        kinder = self.baum.get_children()
        if kinder:
            self.baum.selection_set(kinder[0])

    # -- Aussehen ----------------------------------------------------------

    def stil_anwenden(self) -> None:
        """Setzt die Farben passend zum aktuellen Hell-/Dunkelmodus.

        ``ttk`` kennt die Modi von CustomTkinter nicht, deshalb muss das nach
        jedem Umschalten erneut passieren.
        """
        stil = ttk.Style()
        try:
            stil.theme_use("clam")  # einziges Theme, das sich voll einfaerben laesst
        except Exception:
            pass

        karton = design.einzelfarbe("karton")
        tief = design.einzelfarbe("karton_tief")
        text = design.einzelfarbe("text")
        leise = design.einzelfarbe("text_leise")
        linie = design.einzelfarbe("linie")
        weich = design.einzelfarbe("akzent_weich")

        stil.configure(
            "Fanshop.Treeview",
            background=karton,
            fieldbackground=karton,
            foreground=text,
            rowheight=design.ZEILENHOEHE,
            borderwidth=0,
            font=(design.schriftfamilie("grotesk"), 10),
        )
        stil.configure(
            "Fanshop.Treeview.Heading",
            background=tief,
            foreground=leise,
            relief="flat",
            borderwidth=0,
            padding=(8, 6),
            font=(design.schriftfamilie("grotesk"), 9, "bold"),
        )
        stil.map(
            "Fanshop.Treeview.Heading",
            background=[("active", tief)],
            foreground=[("active", text)],
        )
        # Markierte Zeile: weiche Goldflaeche statt Vollton - ruhiger zu lesen.
        stil.map(
            "Fanshop.Treeview",
            background=[("selected", weich)],
            foreground=[("selected", text)],
        )
        # Markierung "erledigt": graue Schrift auf gedaempfter Flaeche. Eine
        # Zeile, die man ansieht, braucht keine Fehlermeldung, die man wegklickt.
        self.baum.tag_configure("erledigt", foreground=leise, background=tief)

        stil.configure(
            "Vertical.TScrollbar",
            background=linie,
            troughcolor=karton,
            borderwidth=0,
            arrowcolor=leise,
        )
        self.leer_hinweis.configure(text_color=farbe("text_leise"))


# ---------------------------------------------------------------------------
# Dialoge (/NF11/)
# ---------------------------------------------------------------------------

class Dialog(ctk.CTkToplevel):
    """Ein modales Fenster: stellt eine Aussage oder eine Frage.

    Ein Dialog hat höchstens zwei Antworten und lässt sich immer mit Escape
    schließen.
    """

    def __init__(
        self,
        master,
        titel: str,
        nachricht: str,
        art: str = "hinweis",          # "hinweis" | "fehler" | "frage" | "erfolg"
        ja_text: str = "OK",
        nein_text: str = "Abbrechen",
        bilder: list[Path] | None = None,
        bild_beschriftungen: list[str] | None = None,
        grosse_zahl: str = "",
    ) -> None:
        """Baut ein modales Fenster und wartet, bis es geschlossen wird."""
        super().__init__(master)

        self.antwort = False
        self._bild_referenzen = []     # verhindert, dass Tkinter die Bilder verwirft

        self.title(titel)
        self.resizable(False, False)
        self.configure(fg_color=farbe("karton"))
        self.transient(master)

        rahmen = ctk.CTkFrame(self, fg_color="transparent")
        rahmen.pack(fill="both", expand=True, padx=ABSTAND["lg"], pady=ABSTAND["lg"])

        titelfarbe = {
            "fehler": farbe("fehler"),
            "erfolg": farbe("erfolg"),
        }.get(art, farbe("text"))

        ctk.CTkLabel(
            rahmen,
            text=titel,
            font=schrift("titel_gross"),
            text_color=titelfarbe,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, ABSTAND["sm"]))

        if grosse_zahl:
            ctk.CTkLabel(
                rahmen,
                text=grosse_zahl,
                font=schrift("zahl_gross"),
                text_color=farbe("text"),
            ).pack(pady=(0, ABSTAND["sm"]))

        if bilder:
            self._bilder_anzeigen(rahmen, bilder, bild_beschriftungen or [])

        ctk.CTkLabel(
            rahmen,
            text=nachricht,
            font=schrift("text"),
            text_color=farbe("text"),
            wraplength=420,
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(0, ABSTAND["md"]))

        knopfleiste = ctk.CTkFrame(rahmen, fg_color="transparent")
        knopfleiste.pack(fill="x")

        if art == "frage":
            knopf(knopfleiste, nein_text, self._abbrechen).pack(side="right")
            aktionsknopf(knopfleiste, ja_text, self._bestaetigen, breite=150).pack(
                side="right", padx=(0, ABSTAND["sm"])
            )
        else:
            aktionsknopf(knopfleiste, ja_text, self._bestaetigen, breite=150).pack(
                side="right"
            )

        self.bind("<Escape>", lambda ereignis: self._abbrechen())
        self.bind("<Return>", lambda ereignis: self._bestaetigen())

        self._mittig_setzen(master)
        self.grab_set()          # blockiert das Hauptfenster
        self.focus_force()
        self.wait_window()       # wartet, bis der Dialog geschlossen ist

    def _bilder_anzeigen(self, rahmen, pfade: list[Path], beschriftungen: list[str]) -> None:
        """Zeigt eine Reihe von Bildern nebeneinander - z. B. die Sticker eines Kaufs (/F53/)."""
        reihe = ctk.CTkFrame(rahmen, fg_color="transparent")
        reihe.pack(pady=(0, ABSTAND["md"]))

        for nummer, pfad in enumerate(pfade):
            spalte = ctk.CTkFrame(reihe, fg_color="transparent")
            spalte.pack(side="left", padx=ABSTAND["xs"])

            bild = bild_laden(Path(pfad), 132, 99)
            if bild is None:
                continue
            self._bild_referenzen.append(bild)
            ctk.CTkLabel(spalte, image=bild, text="").pack()

            if nummer < len(beschriftungen):
                ctk.CTkLabel(
                    spalte,
                    text=beschriftungen[nummer],
                    font=schrift("label"),
                    text_color=farbe("text_leise"),
                ).pack(pady=(ABSTAND["xs"], 0))

    def _mittig_setzen(self, master) -> None:
        """Setzt das Fenster mittig ueber das Hauptfenster."""
        self.update_idletasks()
        try:
            x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
            y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

    def _bestaetigen(self) -> None:
        """Schliesst den Dialog mit Ja."""
        self.antwort = True
        self.grab_release()
        self.destroy()

    def _abbrechen(self) -> None:
        """Schliesst den Dialog mit Nein."""
        self.antwort = False
        self.grab_release()
        self.destroy()


def hinweis_zeigen(master, titel: str, nachricht: str) -> None:
    """Einfache Meldung mit einem OK-Knopf."""
    Dialog(master, titel, nachricht, art="hinweis")


def fehler_zeigen(master, fehler) -> None:
    """Zeigt einen ``FanshopFehler`` im Dialogfenster (/NF11/).

    Der Meldungstext kommt unverändert aus der Logikschicht - so steht jeder
    Text genau einmal im Projekt.
    """
    Dialog(master, "Das hat nicht geklappt", str(fehler), art="fehler")


def erfolg_zeigen(master, titel: str, nachricht: str) -> None:
    """Meldung mit gruenem Erfolgszeichen und einem OK-Knopf."""
    Dialog(master, titel, nachricht, art="erfolg")


def frage_stellen(master, titel: str, nachricht: str, ja_text: str = "Ja") -> bool:
    """Sicherheitsabfrage vor unwiderruflichen Aktionen.

    :return: True, wenn der Bediener bestätigt hat
    """
    dialog = Dialog(master, titel, nachricht, art="frage", ja_text=ja_text)
    return dialog.antwort
