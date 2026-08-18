#main.py  –  Einstiegspunkt der Anwendung
#WI Fanshop · htw saar · WINF-B25-450 · Gruppe 10

from app import FanshopApp


def main():
    """Erzeugt das Hauptfenster und startet die Ereignisschleife."""
    app = FanshopApp()
    app.mainloop()


if __name__ == "__main__":
    main()