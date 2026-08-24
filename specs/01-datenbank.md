# Spec 01 — Datenbankschicht

**Status:** fertig
**Meilenstein:** 1 (Datenbankschicht, Soll 20.07.2026)
**Anforderungen:** /NF30/, Pflichtenheft Kapitel 6

## Ziel

SQLite-Datei anlegen, Tabellen erzeugen, eine einzige Klasse für allen
Datenbankzugriff bereitstellen.

## Dateien

| Datei | Zweck |
|---|---|
| `fanshop/datenbank/schema.sql` | alle `CREATE TABLE`-Anweisungen |
| `fanshop/datenbank/verbindung.py` | Klasse `Datenbank`, Funktion `datenbank_vorbereiten()` |

## Tabellen

Stammdaten: `kunde`, `artikel`, `sonderaktion`
Bewegungsdaten: `bestellung`, `bestellposition`, `retoure`

Alle Tabellen entsprechen Kapitel 6 des Pflichtenhefts. **Drei Abweichungen**
(siehe `docs/Architektur.md`, Abschnitt Abweichungen):

1. `artikel.groesse TEXT` — zusätzliches Merkmal für Damen/Herren. Das Lastenheft
   verlangt kategorieabhängige Merkmale; ohne diese Spalte gäbe es keine
   sinnvolle Vererbung im Datenmodell.
2. `artikel.bildpfad TEXT` — Dateiname des Produktfotos in `assets/artikel/`.
3. Tabelle `sonderaktion` — das Lastenheft fordert aktivierbare Spezialangebote.
   Ohne Tabelle würde der Aktivierungsstatus einen Neustart nicht überleben.

## Wichtige Details

- `PRAGMA foreign_keys = ON` wird bei jeder Verbindung gesetzt. SQLite prüft
  Fremdschlüssel sonst **nicht**.
- `row_factory = sqlite3.Row` erlaubt `zeile["titel"]` statt `zeile[2]`.
- `CREATE TABLE IF NOT EXISTS` — ein zweiter Programmstart löscht nichts.
- `Datenbank._schema_nachziehen()` ergänzt beim Start Spalten, die es in
  älteren Datenbankdateien noch nicht gab (`kunde.starterset_erhalten`,
  `bestellung.starterset_ausgegeben`), und stellt das Sammelalbum auf die Regel
  „jeder Sticker einmalig" um. `CREATE TABLE IF NOT EXISTS` allein würde
  bestehende Tabellen unverändert lassen — eine benutzte `fanshop.db` müsste
  sonst gelöscht werden.
- `Datenbank.transaktion()` ist ein Kontextmanager: entweder alle Schreibbefehle
  im `with`-Block gelingen, oder SQLite macht alle rückgängig (/NF30/).

## Test

`tests/test_datenbank.py` — Schema anlegen, doppeltes Anlegen ist harmlos,
Fremdschlüssel sind aktiv, Transaktion rollt bei einem Fehler zurück, und eine
Datenbank im alten Format wird beim Start sauber nachgezogen.

## Nächster Schritt

Spec 02 — Fachklassen.
