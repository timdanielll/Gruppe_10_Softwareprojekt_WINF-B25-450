# Spec 02 — Fachklassen (Modelle)

**Status:** fertig
**Meilenstein:** 2 (Geschäftslogik)
**Anforderungen:** /NF20/ (OOD, Vererbung, Kapselung), Kapitel 6

## Ziel

Die Begriffe des Pflichtenhefts als Python-Klassen abbilden. Diese Klassen
kennen weder SQL noch die Oberfläche.

## Dateien

| Datei | Klassen |
|---|---|
| `modelle/artikel.py` | `Artikel`, `Kleidungsartikel(Artikel)` |
| `modelle/kunde.py` | `Kunde` |
| `modelle/bestellung.py` | `Bestellung`, `Bestellposition` |
| `modelle/retoure.py` | `Retoure` |
| `modelle/sticker.py` | `Stickermotiv`, `MOTIVE`, `motive_fuer_kauf()`, `offene_motive()` |
| `modelle/starterset.py` | `INHALT`, `anspruch_besteht()` — das Sonderangebot zur vollen Sammlung |
| `modelle/sonderaktion.py` | `Sonderaktion` |
| `modelle/warenkorb.py` | `Warenkorb`, `WarenkorbPosition`, `Preisuebersicht` |

## Vererbung (/NF20/)

Es gibt drei echte Hierarchien im Projekt — keine davon ist künstlich:

1. **`Artikel` → `Kleidungsartikel`**
   Lastenheft: "Artikel haben in Abhängigkeit ihrer Kategorie weitere Merkmale
   (Herren / Damen, Größe etc.)". `Kleidungsartikel` kennt die Größenspanne
   seiner Kategorie (Damen S–XL, Herren S–5XL) und überschreibt drei Stellen:
   - `groessen` — die wählbaren Größen, aus `GROESSEN_JE_KATEGORIE`.
   - `merkmale()` — die GUI ruft immer nur `artikel.merkmale()` auf und muss
     nicht wissen, welche Artikelart vorliegt (Polymorphie).
   - `groesse_pruefen()` — nimmt nur Größen dieser Kategorie an.
   Welche Klasse entsteht, entscheidet die Fabrikmethode `Artikel.aus_zeile()`
   anhand der Kategorie. Die **gewählte** Größe steht nicht am Artikel, sondern
   an der Warenkorbzeile und später an der Bestellposition.
2. **`BasisRepository` → alle fünf Repositories** (siehe Spec 03).
3. **`BasisSeite` → alle fünf GUI-Seiten** (siehe Spec 08).

## Preisberechnung (/F13/)

Steht vollständig in `Warenkorb.berechne()` und nirgendwo sonst. Feste
Reihenfolge, jeder Schritt rechnet auf dem Ergebnis des vorherigen:

1. **Artikelrabatt** je Position (`artikel.rabattsatz`)
2. **Sonderaktion** — entweder auf die Positionen einer Kategorie oder auf die
   ganze Zwischensumme ab einem Mindestbestellwert
3. **Newsletter-Willkommensrabatt** 10 % auf den Restbetrag (/F52/)

Ergebnis ist ein `Preisuebersicht`-Objekt mit allen Einzelbeträgen — die GUI
beschriftet damit jede Zeile der Summenanzeige, ohne selbst zu rechnen.

Warum diese Reihenfolge? Sie ist unabhängig davon, in welcher Reihenfolge die
Artikel in den Korb gelegt wurden, und der Kunde kann nie mehr als 100 % Rabatt
bekommen.

## Umwandlung Datenbank ↔ Objekt

Jede Klasse hat dasselbe Paar:

- `aus_zeile(zeile)` — Klassenmethode, baut das Objekt aus einer `sqlite3.Row`
- `als_datenbankwerte()` — liefert die Felder als Tupel in Spaltenreihenfolge

Das hält die SQL-Anweisungen in den Repositories kurz.

## Test

`tests/test_warenkorb.py` — Bestandsprüfung beim Hinzufügen, Mengenänderung,
alle drei Rabattarten einzeln und kombiniert.

## Nächster Schritt

Spec 03 — Repositories.
