"""Zentrale Konstanten und Pfade des WI Fanshop.

Alles, was an einer einzigen Stelle konfigurierbar sein soll (Pfade, Kategorien,
Rabattsaetze), steht hier. So muss niemand im restlichen Quellcode nach
"magischen Zahlen" suchen.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
# konfiguration.py liegt in <Projekt>/fanshop/, deshalb zweimal nach oben.
PROJEKT_VERZEICHNIS = Path(__file__).resolve().parent.parent

DATENBANK_DATEI = PROJEKT_VERZEICHNIS / "fanshop.db"
SCHEMA_DATEI = PROJEKT_VERZEICHNIS / "fanshop" / "datenbank" / "schema.sql"

ASSETS_VERZEICHNIS = PROJEKT_VERZEICHNIS / "assets"
ARTIKELBILDER_VERZEICHNIS = ASSETS_VERZEICHNIS / "artikel"
STICKER_VERZEICHNIS = ASSETS_VERZEICHNIS / "sticker"

# ---------------------------------------------------------------------------
# Fachliche Konstanten (Pflichtenheft Kapitel 3 und 6)
# ---------------------------------------------------------------------------

# Die Kategorien sind fest vorgegeben und zur Laufzeit nicht aenderbar
# (Lastenheft: "Die Kategorien koennen zur Laufzeit nicht veraendert werden").
KATEGORIEN = (
    "Damen",
    "Herren",
    "Accessoires",
    "Schreibwaren",
    "Print",
    "Specials",
    "Tickets",
)

# Fuer diese Kategorien gibt es das zusaetzliche Merkmal "Groesse".
# Sie werden im Programm durch die Klasse Kleidungsartikel abgebildet.
KLEIDUNGS_KATEGORIEN = ("Damen", "Herren")

GROESSEN = ("XS", "S", "M", "L", "XL", "XXL")

# Willkommensrabatt fuer die Newsletter-Anmeldung (/F52/): 10 Prozent.
NEWSLETTER_RABATTSATZ = 0.10

# Anzahl der Sticker, die pro abgeschlossenem Einkauf gratis ausgegeben werden (/F53/).
STICKER_PRO_EINKAUF = 3

# Anzeigetext, wenn eine Bestellung keinem Kunden mehr zugeordnet ist (/F43/).
ANONYMER_KUNDE = "Geloeschter Kunde"
