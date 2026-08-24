# Spec 04 — Geschäftslogik (Services)

**Status:** fertig
**Meilenstein:** 2 (Geschäftslogik, Soll 10.08.2026)
**Anforderungen:** /F11/–/F14/, /F21/–/F25/, /F31/–/F313/, /F41/–/F44/, /F51/, /F52/, /F53/, /NF21/

## Ziel

Alle Regeln und Prüfungen an einer Stelle, unabhängig von der Oberfläche
lauffähig und testbar.

## Dateien

| Datei | Klasse | Zuständig für |
|---|---|---|
| `logik/artikel_service.py` | `ArtikelService` | Sortiment: anlegen, pflegen, suchen, Auswertungen |
| `logik/kunden_service.py` | `KundenService` | Kundenkartei, Newsletter-Anmeldung |
| `logik/kassen_service.py` | `KassenService`, `Kaufbeleg` | der Kassiervorgang |
| `logik/retouren_service.py` | `RetourenService` | Rückgaben |
| `logik/bericht_service.py` | `BerichtService`, `Bericht` | Auswertungen für die Shop-Leitung |
| `logik/sonderaktion_service.py` | `SonderaktionService` | Spezialangebote starten und beenden |
| `logik/anwendung.py` | `Anwendung` | steckt alle Schichten zusammen |

## `Anwendung` — der Zusammenbau

Ein Objekt hält Datenbank, alle Repositories und alle Services. Die GUI bekommt
genau dieses eine Objekt und holt sich daraus, was sie braucht. Für einen Test
genügt:

```python
anwendung = Anwendung(datenbank_pfad=":memory:", testdaten=False)
```

Damit läuft die komplette Logik ohne Fenster — das ist der Nachweis für /NF21/.

## `KassenService` — der lineare Ablauf aus /NF12/

```
kunde_waehlen -> artikel_hinzufuegen -> preisuebersicht -> kauf_abschliessen
```

Der Service hält den Zustand **einer** Bedienung: aktiver Kunde, Warenkorb,
Newsletter-Gutschein ja/nein. Das entspricht Kapitel 2.3 des Pflichtenhefts
("genau ein aktiver Kunde pro Sitzung").

Zwei Details, die im Alltag wichtig sind:

- `artikel_hinzufuegen()` nimmt bei Kleidung eine **Größe** entgegen und lädt
  den Artikel **frisch aus der Datenbank**. Der
  Lagerbestand kann sich seit dem Aufbau der Artikelliste geändert haben, etwa
  durch eine Retoure am anderen Ende des Programms.
- `kauf_abschliessen()` prüft **vor** dem Buchen noch einmal jeden Bestand.
  Zwischen "in den Korb legen" und "kassieren" liegen im Laden manchmal
  Minuten.

Verkauf ohne Kundenprofil ist erlaubt (Laufkundschaft) — dann gibt es keine
Sticker, kein Starterset und keinen Newsletter-Rabatt.

- `_praemien_bestimmen()` entscheidet, welche Sammelsticker dieser Kauf bringt
  und ob das Starterset beiliegt. Es liest dafür **das Album**, nicht den
  Zähler — so kann kein Motiv doppelt herausgehen. Details in
  `specs/09-sticker.md`.
- `KundenService.starterset_stand()` liefert der Kartei, wo ein Kunde beim
  Sonderangebot steht (erhalten, oder wie viele Einkäufe noch fehlen).
- `RetourenService.retoure_buchen()` arbeitet mit der **Positionsnummer**, nicht
  mit der Artikelnummer: Derselbe Artikel kann in zwei Größen in einer
  Bestellung stehen.

## Fehlerbehandlung (/NF11/)

Die Logik öffnet **nie** ein Dialogfenster. Sie wirft statt dessen einen Fehler
aus `fanshop/fehler.py` mit einem fertigen deutschen Text:

```
FanshopFehler
├── ValidierungsFehler    Eingabe unvollständig oder unplausibel
├── BestandsFehler        Lagerbestand reicht nicht (/F11/)
└── NichtGefundenFehler   Datensatz existiert nicht
```

Die GUI fängt nur `FanshopFehler` und zeigt `str(fehler)` im Pop-up. Dadurch
steht jeder Meldungstext genau einmal im Projekt — dort, wo das Problem
festgestellt wird.

## Berichte (/F31/)

`zeitraum_schnellwahl("gesamt" | "tag" | "woche" | "monat")` und
`zeitraum_aus_datum("2026-08-01", "2026-08-20")` liefern beide ein Paar
Zeitstempel. Beim Enddatum zählt der **ganze Tag** mit (23:59:59), sonst würde
ein Bericht "vom 1. bis 1. August" leer bleiben.

Über das Pflichtenheft hinaus weist der Bericht neben dem Umsatz (/F312/) auch
Erstattungen und Nettoumsatz aus — ein Bericht, der nur Bruttoumsatz zeigt,
verschweigt zurückgezahltes Geld.

## Test

`tests/test_kasse.py`, `tests/test_artikel_und_kunden.py`,
`tests/test_retouren_und_berichte.py`, `tests/test_sonderaktionen.py`,
`tests/test_sticker.py`.

## Nächster Schritt

Spec 05 — Testdaten.
