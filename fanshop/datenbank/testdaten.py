"""Testdaten fuer die Entwicklung (Pflichtenheft Kapitel 8.2).

Beim allerersten Start ist die Datenbank leer. Damit niemand von Hand Artikel
und Kunden eintippen muss, legt ``testdaten_anlegen()`` einen kompletten
Beispielshop an:

* alle Artikel aus ``assets/artikel/katalog.json`` (echte Fotos aus dem
  htw-saar-Webshop) - ersatzweise sechs fest eingebaute Artikel
* fuenf Testkunden, davon zwei mit Newsletter-Gutschein
* zwei vordefinierte Sonderaktionen (eine davon aktiv)
* einige Beispielbestellungen der letzten Wochen, damit die Berichte und
  Diagramme sofort etwas anzeigen

Die Funktion tut **nichts**, wenn bereits Artikel vorhanden sind. Ein
Programmstart ueberschreibt also niemals echte Daten.
"""

import json

from fanshop import konfiguration
from fanshop.datenbank.verbindung import Datenbank
from fanshop.hilfsmittel import heute_iso, jetzt_zeitstempel, runde_geld
from fanshop.modelle.sticker import motive_fuer_kauf

SEKUNDEN_PRO_TAG = 24 * 60 * 60

# Ersatzsortiment, falls assets/artikel/katalog.json fehlt.
# (titel, kategorie, preis, beschreibung, groesse)
ERSATZ_ARTIKEL = [
    ("Schlüsselband htw saar", "Accessoires", 4.90, "Buntes Schlüsselband mit Karabinerhaken.", ""),
    ("Bleistift Fakultäten", "Schreibwaren", 1.50, "Bleistift im Design der vier Fakultäten.", ""),
    ("Regenschirm Fakultäten", "Accessoires", 19.90, "Stockschirm in den Farben der Hochschule.", ""),
    ("T-Shirt htw saar, schwarz", "Herren", 19.90, "Baumwoll-T-Shirt mit weißem Aufdruck.", "L"),
    ("T-Shirt htw saar, weiß", "Damen", 19.90, "Tailliertes Baumwoll-T-Shirt.", "M"),
    ("Tasse htw saar", "Accessoires", 9.90, "Keramiktasse, spülmaschinenfest.", ""),
]

# Fuenf Testkunden (name, strasse, plz, ort, newsletter)
TEST_KUNDEN = [
    ("Anna Becker", "Waldhausweg 14", 66123, "Saarbrücken", True),
    ("Ben Hoffmann", "Goebenstraße 40", 66117, "Saarbrücken", False),
    ("Clara Schmitt", "Malstatter Straße 7", 66115, "Saarbrücken", True),
    ("David Wagner", "Am Markt 3", 66663, "Merzig", False),
    ("Elif Yildirim", "Bahnhofstraße 22", 66538, "Neunkirchen", False),
]

# Zwei fest definierte Spezialangebote
# (titel, art, zielkategorie, mindestbestellwert, rabattsatz, aktiv)
TEST_AKTIONEN = [
    ("Semesterstart: 20 % auf Schreibwaren", "kategorie", "Schreibwaren", 0.0, 0.20, True),
    ("Ab 50 € Einkaufswert: 10 % auf alles", "mindestwert", None, 50.0, 0.10, False),
]


def _artikel_aus_katalog() -> list[dict]:
    """Liest die katalogisierten Produktfotos, falls vorhanden."""
    katalog_datei = konfiguration.ARTIKELBILDER_VERZEICHNIS / "katalog.json"
    if not katalog_datei.exists():
        return []
    try:
        return json.loads(katalog_datei.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Kaputte Datei soll den Programmstart nicht verhindern.
        return []


def testdaten_anlegen(datenbank: Datenbank, mit_bestellungen: bool = True) -> bool:
    """Fuellt eine leere Datenbank mit Beispieldaten.

    :param mit_bestellungen: legt zusaetzlich Beispielbestellungen an, damit
                             die Berichte nicht leer sind
    :return: True, wenn Daten angelegt wurden; False, wenn schon welche da waren
    """
    vorhandene = datenbank.abfragen_eine("SELECT COUNT(*) AS n FROM artikel")
    if vorhandene and vorhandene["n"] > 0:
        return False

    _artikel_anlegen(datenbank)
    _kunden_anlegen(datenbank)
    _aktionen_anlegen(datenbank)
    if mit_bestellungen:
        _bestellungen_anlegen(datenbank)
    return True


def _artikel_anlegen(datenbank: Datenbank) -> None:
    katalog = _artikel_aus_katalog()
    heute = heute_iso()
    zeilen = []

    if katalog:
        for nummer, eintrag in enumerate(katalog):
            # Lagerbestand und Rabatt werden nach einem festen Muster vergeben,
            # damit die Testdaten bei jedem Rechner identisch aussehen.
            lagerbestand = 5 + (nummer * 7) % 26
            rabattsatz = 0.15 if nummer % 5 == 0 else 0.0
            zeilen.append(
                (
                    eintrag["kategorie"],
                    eintrag["titel"],
                    eintrag.get("beschreibung", ""),
                    float(eintrag["preis"]),
                    rabattsatz,
                    lagerbestand,
                    heute,
                    1,
                    eintrag.get("groesse") or None,
                    eintrag.get("datei"),
                )
            )
    else:
        for nummer, (titel, kategorie, preis, beschreibung, groesse) in enumerate(ERSATZ_ARTIKEL):
            zeilen.append(
                (
                    kategorie,
                    titel,
                    beschreibung,
                    preis,
                    0.15 if nummer % 5 == 0 else 0.0,
                    5 + (nummer * 7) % 26,
                    heute,
                    1,
                    groesse or None,
                    None,
                )
            )

    datenbank.ausfuehren_viele(
        """INSERT INTO artikel
               (kategorie, titel, beschreibung, preis, rabattsatz,
                lagerbestand, erstellungsdatum, aktiv, groesse, bildpfad)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        zeilen,
    )


def _kunden_anlegen(datenbank: Datenbank) -> None:
    zeilen = [
        (name, strasse, plz, ort, 1 if newsletter else 0, 1 if newsletter else 0, 0)
        for name, strasse, plz, ort, newsletter in TEST_KUNDEN
    ]
    datenbank.ausfuehren_viele(
        """INSERT INTO kunde
               (name, strasse, plz, ort, newsletter_aktiv,
                newsletter_rabatt_verfuegbar, sticker_kontostand)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        zeilen,
    )


def _aktionen_anlegen(datenbank: Datenbank) -> None:
    zeilen = [
        (titel, art, ziel, mindestwert, rabatt, 1 if aktiv else 0)
        for titel, art, ziel, mindestwert, rabatt, aktiv in TEST_AKTIONEN
    ]
    datenbank.ausfuehren_viele(
        """INSERT INTO sonderaktion
               (titel, art, zielkategorie, mindestbestellwert, rabattsatz, aktiv)
           VALUES (?, ?, ?, ?, ?, ?)""",
        zeilen,
    )


def _bestellungen_anlegen(datenbank: Datenbank) -> None:
    """Legt acht Beispielbestellungen der letzten drei Wochen an.

    Diese Bestellungen werden direkt geschrieben und nicht ueber den
    KassenService gebucht - nur so lassen sich Zeitstempel in der
    Vergangenheit setzen, damit die Zeitraumfilter der Berichte etwas zu
    filtern haben.
    """
    artikel = datenbank.abfragen(
        "SELECT artikel_id, preis, rabattsatz, lagerbestand FROM artikel ORDER BY artikel_id"
    )
    kunden = datenbank.abfragen("SELECT kundennummer FROM kunde ORDER BY kundennummer")
    if not artikel or not kunden:
        return

    jetzt = jetzt_zeitstempel()

    # Merkt sich je Kunde, wie viele Sticker er schon hat - daraus ergibt sich,
    # welche Motive der naechste Einkauf bringt (siehe modelle/sticker.py).
    stickerstand: dict[int, int] = {}

    # (Tage in der Vergangenheit, Indizes der Artikel, Mengen, Kundenindex)
    bausteine = [
        (20, [0, 1], [1, 2], 0),
        (17, [2], [1], 1),
        (14, [0, 3], [2, 1], 2),
        (10, [1, 2, 3], [1, 1, 1], 3),
        (7, [4], [3], 4),
        (4, [0, 4], [1, 1], 0),
        (2, [2, 3], [2, 1], 1),
        (1, [1], [4], 2),
    ]

    with datenbank.transaktion() as verbindung:
        for tage, artikel_indizes, mengen, kundenindex in bausteine:
            positionen = []
            gesamtbetrag = 0.0

            for index, menge in zip(artikel_indizes, mengen):
                zeile = artikel[index % len(artikel)]
                einzelpreis = runde_geld(zeile["preis"] * (1 - zeile["rabattsatz"]))
                positionen.append((zeile["artikel_id"], menge, einzelpreis))
                gesamtbetrag += einzelpreis * menge

            gesamtbetrag = runde_geld(gesamtbetrag)
            kundennummer = kunden[kundenindex % len(kunden)]["kundennummer"]

            cursor = verbindung.execute(
                """INSERT INTO bestellung
                       (kundennummer, zeitstempel, gesamtbetrag,
                        newsletter_rabatt_angewendet, sticker_ausgegeben)
                   VALUES (?, ?, ?, 0, ?)""",
                (
                    kundennummer,
                    jetzt - tage * SEKUNDEN_PRO_TAG,
                    gesamtbetrag,
                    konfiguration.STICKER_PRO_EINKAUF,
                ),
            )
            bestellnummer = cursor.lastrowid

            for artikel_id, menge, einzelpreis in positionen:
                verbindung.execute(
                    """INSERT INTO bestellposition
                           (bestellnummer, artikel_id, menge, historischer_preis)
                       VALUES (?, ?, ?, ?)""",
                    (bestellnummer, artikel_id, menge, einzelpreis),
                )
                verbindung.execute(
                    "UPDATE artikel SET lagerbestand = lagerbestand - ? WHERE artikel_id = ?",
                    (menge, artikel_id),
                )

            verbindung.execute(
                """UPDATE kunde SET sticker_kontostand = sticker_kontostand + ?
                   WHERE kundennummer = ?""",
                (konfiguration.STICKER_PRO_EINKAUF, kundennummer),
            )

            # Dieselben Motive, die auch ein echter Kauf vergeben wuerde.
            vorher = stickerstand.get(kundennummer, 0)
            for motiv in motive_fuer_kauf(vorher, konfiguration.STICKER_PRO_EINKAUF):
                verbindung.execute(
                    """INSERT INTO kunde_sticker (kundennummer, motiv, anzahl)
                       VALUES (?, ?, 1)
                       ON CONFLICT (kundennummer, motiv)
                       DO UPDATE SET anzahl = anzahl + 1""",
                    (kundennummer, motiv.schluessel),
                )
            stickerstand[kundennummer] = vorher + konfiguration.STICKER_PRO_EINKAUF
