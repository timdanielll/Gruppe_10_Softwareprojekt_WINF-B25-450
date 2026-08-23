# Spec 08 — Automatische Tests

**Status:** fertig
**Meilenstein:** 4 (Integration und Testing, Soll 15.09.2026)

## Ziel

Nachweisen, dass die Geschäftslogik stimmt — und zwar ohne Oberfläche. Genau
das ist der Beleg für /NF21/.

## Ausführen

```bash
python -m unittest discover -s tests -t . -v
```

Stand: **91 Tests, alle grün**, Laufzeit unter einer Sekunde.

## Dateien

| Datei | Prüft |
|---|---|
| `tests/basis.py` | Basisklasse: frische Datenbank je Testfall |
| `tests/test_datenbank.py` | Schema, Fremdschlüssel, Transaktionen (/NF30/) |
| `tests/test_warenkorb.py` | Bestandsprüfung und die ganze Rabattrechnung (/F11/–/F13/) |
| `tests/test_kasse.py` | Kaufabschluss, Sticker, Newsletter (/F14/, /F52/, /F53/) |
| `tests/test_artikel_und_kunden.py` | Sortiment und Kartei (/F21/–/F23/, /F41/–/F44/) |
| `tests/test_retouren_und_berichte.py` | Retouren und Auswertungen (/F51/, /F31/–/F313/, /F24/, /F25/) |
| `tests/test_sticker.py` | Sammelalbum: Motivvergabe, Album, Zähler (/F53/) |
| `tests/test_sonderaktionen.py` | Spezialangebote starten, ablösen, beenden |

## Warum `unittest` und nicht `pytest`

`unittest` gehört zur Standardbibliothek. Es muss nichts installiert werden,
und die Tests laufen auf jedem Rechner der Gruppe ohne Vorbereitung. Für den
Umfang dieses Projekts nimmt sich pytest nichts.

## Wie die Tests isoliert bleiben

`FanshopTest.setUp()` legt für **jeden einzelnen** Testfall eine neue Datenbank
im Arbeitsspeicher an (`":memory:"`, `testdaten=False`). Folgen daraus:

- Tests können sich nicht gegenseitig beeinflussen.
- Die echte `fanshop.db` wird nie angefasst.
- Jeder Test legt genau die Daten an, die er braucht — man liest am Test ab,
  welche Vorbedingungen gelten.

## Die Tests, die wirklich etwas fangen

Nicht jeder Test ist gleich viel wert. Diese vier haben beim Bauen Fehler
gefunden oder verhindern die gefährlichsten:

1. `test_alle_drei_rabatte_kumulieren_in_fester_reihenfolge` — rechnet den
   kompletten Rabattpfad von 100,00 € auf 64,80 € nach.
2. `test_historischer_preis_enthaelt_den_gezahlten_betrag` — ohne die
   Verteilung der Warenkorbrabatte auf die Positionen würde eine Retoure mehr
   erstatten, als eingenommen wurde.
3. `test_bestand_wird_vor_dem_buchen_erneut_geprueft` — zwischen „in den Korb"
   und „kassieren" kann sich der Lagerbestand geändert haben.
4. `test_transaktion_wird_bei_einem_fehler_zurueckgerollt` — der direkte
   Nachweis für /NF30/.
5. `test_zaehler_und_album_bleiben_gleich` — `sticker_kontostand` und die
   Summe im Sammelalbum dürfen nie auseinanderlaufen.
6. `test_stickerstand_bleibt_beim_speichern_erhalten` — ein Adressupdate mit
   einem veralteten Kundenobjekt darf den Sammelstand nicht zurücksetzen.
7. `test_postleitzahl_mit_fuehrender_null` — 01067 Dresden muss durchgehen,
   obwohl die Spalte laut Pflichtenheft INTEGER ist.

## Was die Tests nicht abdecken

Die Oberfläche selbst wird nicht automatisch getestet — dafür bräuchte es
Werkzeuge, die den Rahmen des Moduls sprengen. Statt dessen gibt es die
Testfall-Tabelle in `docs/Technische-Dokumentation.md`, die man einmal von Hand
durchklickt.

## Nächster Schritt

Dokumentation und Übergabe an die Gruppe (`docs/Commit-Plan.md`).
