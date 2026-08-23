"""Basisklasse aller Seiten der Anwendung.

Jede der fuenf Seiten (Kasse, Sortiment, Kunden, Retouren, Berichte) erbt von
``BasisSeite``. Dadurch haben alle denselben Aufbau und dieselben drei
Einstiegspunkte - man muss eine Seite nur einmal verstanden haben:

* ``aufbauen()``        wird **einmal** aufgerufen und legt die Widgets an
* ``beim_anzeigen()``   wird bei **jedem** Wechsel auf diese Seite aufgerufen
                        und laedt frische Daten
* ``stil_aktualisieren()`` wird nach dem Umschalten zwischen Hell und Dunkel
                        aufgerufen

Ausserdem bekommt jede Seite eine **Statuszeile** und die Methode ``melden()``.
Damit sagt jede Aktion, dass sie angekommen ist - ohne dass ein Dialogfenster
weggeklickt werden muss.

Das ist die dritte Vererbungshierarchie des Projekts (/NF20/).
"""

import customtkinter as ctk

from fanshop.fehler import FanshopFehler
from fanshop.gui import bausteine
from fanshop.gui.design import ABSTAND


class BasisSeite(ctk.CTkFrame):
    """Gemeinsames Grundgeruest aller Seiten."""

    #: Titel, der oben auf der Seite und in der Navigation steht.
    titel = ""

    def __init__(self, master, anwendung) -> None:
        super().__init__(master, fg_color="transparent")
        self.anwendung = anwendung

        self.kopfzeile = ctk.CTkFrame(self, fg_color="transparent")
        self.kopfzeile.pack(fill="x", pady=(0, ABSTAND["md"]))
        bausteine.Ueberschrift(self.kopfzeile, self.titel).pack(side="left")

        #: Rueckmeldung nach jedem Klick - liegt ganz unten auf der Seite.
        self.statuszeile = bausteine.Statuszeile(self)
        self.statuszeile.pack(side="bottom", fill="x", pady=(ABSTAND["sm"], 0))

        #: Hier bauen die Unterklassen ihren Inhalt hinein.
        self.inhalt = ctk.CTkFrame(self, fg_color="transparent")
        self.inhalt.pack(fill="both", expand=True)

        self.aufbauen()

    # -- von den Unterklassen zu fuellen -----------------------------------

    def aufbauen(self) -> None:
        """Legt die Widgets der Seite an. Muss überschrieben werden."""
        raise NotImplementedError(
            f"{type(self).__name__} muss die Methode aufbauen() überschreiben."
        )

    def beim_anzeigen(self) -> None:
        """Wird bei jedem Wechsel auf diese Seite aufgerufen.

        Standardmäßig passiert nichts. Seiten, die Daten anzeigen,
        überschreiben die Methode und laden dort neu - so sieht der Bediener
        nach einem Verkauf sofort den neuen Lagerbestand.
        """

    def stil_aktualisieren(self) -> None:
        """Wird nach dem Umschalten von Hell auf Dunkel aufgerufen.

        Nur Widgets, die CustomTkinter nicht selbst umfärbt (also die
        Tabellen), müssen hier nachgezogen werden.
        """

    # -- Hilfen fuer alle Seiten -------------------------------------------

    def melden(self, nachricht: str, art: str = "erfolg") -> None:
        """Schreibt eine Rückmeldung in die Statuszeile.

        :param art: ``"erfolg"``, ``"fehler"`` oder ``"neutral"``
        """
        self.statuszeile.melden(nachricht, art)

    def fehler_anzeigen(self, fehler: FanshopFehler) -> None:
        """Zeigt einen fachlichen Fehler im Dialogfenster (/NF11/).

        Zusätzlich landet die Meldung in der Statuszeile - der Dialog
        verschwindet beim Wegklicken, die Zeile bleibt.
        """
        self.melden(str(fehler), art="fehler")
        bausteine.fehler_zeigen(self, fehler)

    def hinweis_anzeigen(self, titel: str, nachricht: str) -> None:
        bausteine.hinweis_zeigen(self, titel, nachricht)

    def frage_stellen(self, titel: str, nachricht: str, ja_text: str = "Ja") -> bool:
        return bausteine.frage_stellen(self, titel, nachricht, ja_text)
