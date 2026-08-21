"""WI Fanshop - Kassensystem und Warenwirtschaft (WINF-B25-450, Gruppe 10).

Das Paket ist in vier Schichten aufgeteilt:

    fanshop.datenbank      Verbindung zur SQLite-Datei und Tabellenschema
    fanshop.modelle        Klassen der Fachobjekte (Artikel, Kunde, Warenkorb ...)
    fanshop.repositories   Datenzugriff (SQL) - liest und schreibt Fachobjekte
    fanshop.logik          Geschaeftslogik (Kasse, Retouren, Berichte)
    fanshop.gui            Benutzeroberflaeche mit CustomTkinter

Wichtig (/NF21/): Die Schichten kennen immer nur die Schicht unter sich.
Die GUI ruft die Logik auf, die Logik ruft die Repositories auf,
die Repositories sprechen mit der Datenbank. Umgekehrt niemals.
"""

__version__ = "1.0.0"
