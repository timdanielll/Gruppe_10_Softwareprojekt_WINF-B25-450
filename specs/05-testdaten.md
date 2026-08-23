# Spec 05 — Testdaten

**Status:** fertig
**Anforderungen:** Pflichtenheft Kapitel 8.2

## Ziel

Beim allerersten Start soll ein vollständiger Beispielshop bereitstehen, damit
niemand für jeden Test Artikel und Kunden von Hand eintippt.

## Datei

`fanshop/datenbank/testdaten.py` — Funktion `testdaten_anlegen(datenbank)`.

## Was angelegt wird

| Menge | Was | Quelle |
|---|---|---|
| 31 | Artikel mit echten Produktfotos | `assets/artikel/katalog.json` |
| 5 | Kunden, davon 2 mit Newsletter-Gutschein | fest im Code |
| 2 | Sonderaktionen (eine aktiv) | fest im Code |
| 8 | Beispielbestellungen der letzten drei Wochen | fest im Code |

Gefordert waren mindestens 5 Artikel und 3 Kunden — beides ist deutlich
übererfüllt, weil die echten Fotos ohnehin im Repository liegen.

## Wichtige Eigenschaften

- **Läuft nur einmal.** Sind schon Artikel vorhanden, tut die Funktion nichts.
  Ein Programmstart kann also niemals echte Daten überschreiben.
- **Immer dieselben Werte.** Lagerbestände und Rabatte entstehen aus einer
  festen Formel (`5 + (nummer * 7) % 26`) und nicht per Zufall. Auf jedem
  Rechner der Gruppe sieht die Datenbank dadurch identisch aus — sonst lassen
  sich Fehler nicht vergleichen.
- **Fällt weich zurück.** Fehlt `katalog.json` oder ist sie beschädigt, werden
  sechs fest eingebaute Artikel angelegt. Der Programmstart scheitert nie an
  einer fehlenden Assetdatei.

## Warum es Beispielbestellungen gibt

Ohne Bestellungen sind alle Berichte leer und die Diagramme (/F26/, /F27/)
nicht überprüfbar. Die acht Bestellungen werden direkt per SQL geschrieben und
**nicht** über den `KassenService` gebucht — nur so lassen sich Zeitstempel in
der Vergangenheit setzen, damit die Zeitraumfilter etwas zu filtern haben.

## Artikelkatalog

`assets/artikel/katalog.json` ordnet jedem der 31 Fotos Titel, Kategorie,
Größe, Beschreibung und Preis zu. Die Datei ist reine Datenhaltung — wer einen
Artikel umbenennen oder umkategorisieren will, ändert nur diese Datei und
löscht `fanshop.db`.

## Nächster Schritt

Spec 06 — Designsystem.
