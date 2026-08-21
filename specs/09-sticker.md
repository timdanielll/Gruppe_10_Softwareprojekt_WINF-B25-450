# Spec 09 — Sticker-Sammelsystem

**Status:** fertig
**Anforderungen:** /F53/ (Kann-Kriterium)

## Ziel

Aus dem Zähler `kunde.sticker_kontostand` eine echte **Sammlung** machen — das
ist der Punkt, an dem ein Gamification-Modul steht oder fällt.

## Die Frage, die dahinter stand

Das Pflichtenheft sagt: „bucht das System automatisch 3 Sticker kostenlos auf
das Kundenkonto." Im Assets-Ordner liegen aber **sechs verschiedene Motive**
(`assets/sticker/`). Dreimal dasselbe Bild auszugeben wäre die wörtlichste,
aber langweiligste Lesart. Umgesetzt ist deshalb: **drei verschiedene Motive
pro Einkauf**, der Reihe nach vergeben.

## Dateien

| Datei | Inhalt |
|---|---|
| `fanshop/modelle/sticker.py` | `Stickermotiv`, die Liste `MOTIVE`, `motive_fuer_kauf()`, `album_fortschritt()` |
| `fanshop/datenbank/schema.sql` | Tabelle `kunde_sticker` |
| `fanshop/repositories/kunden_repository.py` | `sticker_album()` |
| `fanshop/repositories/bestell_repository.py` | schreibt die Motive beim Kauf mit |
| `fanshop/logik/kassen_service.py` | bestimmt die Motive, füllt den `Kaufbeleg` |
| `fanshop/gui/bausteine.py` | `StickerAlbum` — die sechs Motive nebeneinander |
| `tests/test_sticker.py` | 13 Tests |

## Die sechs Motive

`campus` · `htwsaar` · `kneipe` · `liebt` · `mensen` · `vier`

Die Reihenfolge in `MOTIVE` ist **nicht beliebig** — sie bestimmt die Ausgabe.

## Vergabe: reihum, nicht zufällig

```python
start = bisheriger_kontostand % 6
motive = [MOTIVE[(start + n) % 6] for n in range(3)]
```

Zwei Gründe gegen einen Zufallsgenerator:

1. **Nach zwei Einkäufen ist das Album garantiert einmal komplett.** Bei Zufall
   könnte ein Kunde fünfmal dasselbe Motiv ziehen — das frustriert statt zu
   binden.
2. **Wiederholbarkeit.** Ein Zufallswert macht jeden Test unzuverlässig. Mit
   der festen Reihenfolge prüft `tests/test_sticker.py` exakte Motivlisten.

## Datenmodell

```sql
CREATE TABLE kunde_sticker (
    kundennummer INTEGER NOT NULL,
    motiv        TEXT    NOT NULL,
    anzahl       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (kundennummer, motiv),
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE CASCADE
);
```

Das ist die **vierte Abweichung** vom Pflichtenheft (siehe
`docs/Architektur.md`, Kapitel 7). Ohne diese Tabelle weiß das System nur, *wie
viele* Sticker jemand hat, nicht *welche* — und dann gibt es keine Sammlung.

`ON DELETE CASCADE` sorgt dafür, dass das Album mit dem Kunden verschwindet
(/F43/). Das ist getestet: `test_album_verschwindet_mit_dem_kunden`.

## Zwei Stände, die zusammenpassen müssen

`kunde.sticker_kontostand` (Zähler, aus dem Pflichtenheft) und die Summe über
`kunde_sticker.anzahl` (Album) sind zwei Darstellungen derselben Sache. Beide
werden in **derselben Transaktion** geschrieben — `kauf_verbuchen()` erhöht den
Zähler und schreibt die Motivzeilen im selben `with`-Block.

Der Test `test_zaehler_und_album_bleiben_gleich` prüft nach drei Einkäufen,
dass beide Zahlen übereinstimmen.

## In der Oberfläche

* **Nach dem Kauf:** Der Dialog zeigt die drei Motive als Bilder mit Titel und
  darunter „Sammlung: 4 von 6 Motiven".
* **Kundenkartei:** Alle sechs Motive nebeneinander — vorhandene in Farbe,
  fehlende grau und aufgehellt (`bild_laden(..., blass=True)`), darunter je die
  Anzahl.
* **Laufkundschaft** bekommt weder Sticker noch Album — ohne Kundenkonto gibt
  es niemanden, dem man etwas gutschreiben könnte.

## Testdaten

`fanshop/datenbank/testdaten.py` füllt die Alben der Beispielbestellungen mit
**derselben** Funktion `motive_fuer_kauf()`, die auch ein echter Kauf benutzt.
Sonst hätten die Testkunden einen Zähler von 6, aber ein leeres Album — und die
Kartei sähe beim ersten Start kaputt aus.
