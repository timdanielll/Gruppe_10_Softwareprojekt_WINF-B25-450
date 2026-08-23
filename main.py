"""Startpunkt des WI Fanshop.

Aufruf:

    python main.py

Was hier passiert - und nur hier:

1. Das htw-saar-Design wird geladen (muss vor dem ersten Fenster geschehen).
2. Die Anwendung wird zusammengebaut: Datenbank, Repositories, Services.
   Beim allerersten Start entstehen dabei Datenbankdatei und Testdaten.
3. Das Hauptfenster wird geöffnet.
"""

from fanshop.gui import design
from fanshop.gui.app import FanshopApp
from fanshop.logik.anwendung import Anwendung


def main() -> None:
    # 1. Design zuerst - CustomTkinter liest das Theme beim Erzeugen der Widgets.
    design.design_aktivieren("light")

    # 2. Logik und Datenbank
    anwendung = Anwendung()
    if anwendung.testdaten_wurden_angelegt:
        print("Neue Datenbank angelegt und mit Testdaten gefüllt:", anwendung.datenbank.pfad)

    # 3. Oberfläche
    fenster = FanshopApp(anwendung)
    fenster.mainloop()


if __name__ == "__main__":
    main()
