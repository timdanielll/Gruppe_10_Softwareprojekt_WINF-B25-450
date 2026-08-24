"""Benutzeroberfläche des WI Fanshop (CustomTkinter).

Die GUI kennt nur die Logikschicht. Sie enthält keine Rechnung und kein SQL —
sie zeigt an, was die Services liefern, und meldet, was der Bediener anklickt.

Aufbau:

    design.py       Farben, Schriften, Abstände (abgeleitet aus DESIGN.md)
    bausteine.py    wiederverwendbare Widgets (Tabelle, Feld, Dialog ...)
    basis_seite.py  gemeinsame Basisklasse aller Seiten
    app.py          Rollenauswahl, Hauptfenster und Navigation
    seite_*.py      die fünf Fachseiten (Kunde: nur Kasse)
"""

from fanshop.gui.app import FanshopApp

__all__ = ["FanshopApp"]
