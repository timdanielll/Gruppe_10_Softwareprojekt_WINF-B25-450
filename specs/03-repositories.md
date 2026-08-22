# Spec 03 — Repositories (Datenzugriff)

**Status:** fertig
**Meilenstein:** 1 (Data Access Objects)
**Anforderungen:** /F21/–/F25/, /F41/–/F44/, /F51/, /F311/–/F313/, /NF30/

## Ziel

Die einzige Stelle im Programm, an der SQL steht.

## Dateien

| Datei | Tabelle | Wichtigste Methoden |
|---|---|---|
| `basis_repository.py` | — | `anzahl`, `existiert`, `loeschen` |
| `artikel_repository.py` | `artikel` | `speichern`, `suchen`, `deaktivieren`, `umsatzstaerkste`, `haeufigste` |
| `kunden_repository.py` | `kunde`, `kunde_sticker` | `speichern`, `suchen`, `loeschen_und_anonymisieren`, `newsletter_setzen`, `sticker_album` |
| `bestell_repository.py` | `bestellung`, `bestellposition`, `retoure` | `kauf_verbuchen`, `retoure_verbuchen`, `positionen_zu` |
| `bericht_repository.py` | Auswertungen | `kennzahlen`, `umsatzanteile`, `umsatz_je_kategorie` |
| `sonderaktion_repository.py` | `sonderaktion` | `aktive`, `aktivieren` |

## Entscheidung: zwei Methoden bündeln mehrere Tabellen

`kauf_verbuchen()` und `retoure_verbuchen()` schreiben in einem Rutsch mehrere
Tabellen — in **einer** Transaktion.

Warum nicht sauber pro Tabelle trennen? Weil ein Kauf für die Datenbank ein
einziger Vorgang ist: Bestellung, Positionen, Lagerabgang, Sticker und
Gutschein gehören zusammen. Bei getrennten Aufrufen könnte nach einem Absturz
eine Bestellung existieren, deren Ware nie aus dem Lager gebucht wurde. Genau
das verbietet /NF30/.

## Entscheidung: `historischer_preis` enthält den wirklich gezahlten Preis

Rabatte auf den ganzen Warenkorb (Sonderaktion, Newsletter) werden beim Buchen
gleichmäßig auf alle Positionen verteilt:

```
faktor = gesamtbetrag / zwischensumme
historischer_preis = einzelpreis * faktor
```

Ohne diese Verteilung würde eine spätere Retoure mehr Geld erstatten, als der
Kunde gezahlt hat.

## Entscheidung: Artikel werden nie gelöscht

`deaktivieren()` setzt `aktiv = 0` (Soft-Delete, /F22/). Alte Bestellungen und
Retouren verweisen auf den Artikel und müssen lesbar bleiben.

Kunden werden dagegen wirklich gelöscht (/F43/) — ihre Bestellungen bekommen
vorher `kundennummer = NULL` und gelten damit als anonymisiert. Beides zusammen
läuft in einer Transaktion.

## Stolperfalle: Zeitzonen bei Retouren

`retoure.retouren_datum` ist laut Pflichtenheft **Text**, `bestellung.zeitstempel`
dagegen eine Unix-Zeit. SQLites `strftime('%s', ...)` deutet Textdaten immer als
UTC und liefert dadurch in Deutschland eine um ein bis zwei Stunden verschobene
Zeit — Retouren fielen so aus dem Berichtszeitraum heraus.

Lösung: Die Zeitraumgrenzen werden in Python mit `zeitstempel_zu_iso()` in Text
umgewandelt und direkt verglichen. ISO-Datumstexte sind alphabetisch sortierbar,
deshalb funktioniert `BETWEEN` auf Text genauso zuverlässig.

## Test

`tests/test_artikel_und_kunden.py` — Suche mit allen Filterkombinationen,
Soft-Delete, Anonymisierung.
`tests/test_retouren_und_berichte.py` — doppelte Retoure wird verhindert.

## Nächster Schritt

Spec 04 — Kassiervorgang.
