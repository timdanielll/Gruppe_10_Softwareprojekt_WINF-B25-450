# Spec 09 — Sticker-Sammelsystem und Starterset

**Status:** fertig
**Anforderungen:** /F53/ (Kann-Kriterium)

## Ziel

Aus dem Zähler `kunde.sticker_kontostand` eine echte **Sammlung** machen — das
ist der Punkt, an dem ein Gamification-Modul steht oder fällt. Und die
Sammlung mit einem Ziel versehen: dem **Starterset**.

## Die Frage, die dahinter stand

Das Pflichtenheft sagt: „bucht das System automatisch Sticker kostenlos auf
das Kundenkonto." Im Assets-Ordner liegen aber **sechs verschiedene Motive**
(`assets/sticker/`). Mehrfach dasselbe Bild auszugeben wäre die wörtlichste,
aber langweiligste Lesart. Umgesetzt ist deshalb: **zwei verschiedene Motive
pro Einkauf**, der Reihe nach vergeben, **jedes Motiv nur ein einziges Mal**.

Sechs Motive geteilt durch zwei pro Kauf ergibt drei Einkäufe bis zur vollen
Sammlung — und genau daran hängt das Starterset.

## Dateien

| Datei | Inhalt |
|---|---|
| `fanshop/modelle/sticker.py` | `Stickermotiv`, die Liste `MOTIVE`, `motive_fuer_kauf()`, `offene_motive()`, `album_fortschritt()`, `album_vollstaendig()` |
| `fanshop/modelle/starterset.py` | `INHALT`, `anspruch_besteht()`, `fehlende_bestellungen()` |
| `fanshop/datenbank/schema.sql` | Tabelle `kunde_sticker`, Spalten `kunde.starterset_erhalten` und `bestellung.starterset_ausgegeben` |
| `fanshop/datenbank/verbindung.py` | `_schema_nachziehen()` — bringt ältere Datenbankdateien auf den neuen Stand |
| `fanshop/repositories/kunden_repository.py` | `sticker_album()`, `starterset_erhalten()` |
| `fanshop/repositories/bestell_repository.py` | schreibt Motive und Starterset beim Kauf mit, `anzahl_bestellungen()` |
| `fanshop/logik/kassen_service.py` | `_praemien_bestimmen()`, füllt den `Kaufbeleg`, `starterset_vorschau()` |
| `fanshop/logik/kunden_service.py` | `StartersetStand` für die Kartei |
| `fanshop/gui/bausteine.py` | `StickerAlbum` — die sechs Motive nebeneinander |
| `tests/test_sticker.py` | 21 Tests |
| `tests/test_starterset.py` | 25 Tests |

## Die sechs Motive

`campus` · `htwsaar` · `kneipe` · `liebt` · `mensen` · `vier`

Die Reihenfolge in `MOTIVE` ist **nicht beliebig** — sie bestimmt die Ausgabe.

## Vergabe: reihum, einmalig, ohne Mindestbestellwert

```python
# Grundregel, am Kontostand abgelesen
motive = MOTIVE[kontostand:kontostand + 2]

# Was der echte Kauf benutzt: die noch fehlenden Motive, in Listenreihenfolge
motive = [m for m in MOTIVE if m.schluessel not in album][:2]
```

Drei Entscheidungen stecken darin:

1. **Kein Zufallsgenerator.** Ein Zufallswert macht jeden Test unzuverlässig.
   Mit der festen Reihenfolge prüft `tests/test_sticker.py` exakte Motivlisten.
   Und ein Kunde, der fünfmal dasselbe Motiv zieht, ist frustriert statt
   gebunden.
2. **Jedes Motiv genau einmal.** Wer alle sechs hat, bekommt keine weiteren
   Sticker mehr — dann greift stattdessen das Starterset. Der Kaufbeleg meldet
   in diesem Fall ehrlich `sticker = 0`.
3. **Kein Mindestbestellwert.** Ein Kauf über einen Cent zählt genauso wie
   einer über hundert Euro. Nur **Laufkundschaft** geht leer aus — ohne
   Kundenkonto gibt es niemanden, dem man etwas gutschreiben könnte.

Die Vergabe am Kaufabschluss liest **das Album**, nicht den Zähler. Selbst wenn
beide Stände einmal auseinanderlaufen sollten, kann so kein Motiv doppelt
herausgehen.

## Das Starterset — ein Sonderangebot, keine Sonderaktion

Wer **drei Einkäufe** getätigt und damit **alle sechs Motive** gesammelt hat,
bekommt einmalig ein Set aus **Stift, Block und Jutebeutel** gratis dazu. Es
wird dem Kundenkonto gutgeschrieben (`kunde.starterset_erhalten`) und der
Bestellung beigelegt (`bestellung.starterset_ausgegeben`) — beides in derselben
Transaktion wie der Kauf selbst.

Alle drei Bedingungen müssen zusammenkommen:

1. es gibt ein Kundenkonto (Laufkundschaft geht leer aus)
2. mindestens drei abgeschlossene Einkäufe, diesen mitgezählt
3. die Sammlung ist nach diesem Kauf vollständig

**Warum kein Eintrag in der Tabelle `sonderaktion`?** Eine `Sonderaktion` ist
ein Rabattsatz, den der Bediener scharf schaltet, und es darf immer nur eine
gleichzeitig laufen. Das Starterset ist beides nicht: Es ist keine
Preisminderung, sondern eine Sachprämie, und es ist ein **Dauerangebot** — es
soll nicht verschwinden, nur weil jemand nebenbei „20 % auf Schreibwaren"
startet. Deshalb steht es als eigene Fachregel in `modelle/starterset.py` und
erscheint in der Oberfläche unter den Sonderaktionen als fester Hinweis auf ein
dauerhaftes Sonderangebot.

Auch hier gilt **kein Mindestbestellwert** — es zählt allein die Zahl der
Einkäufe.

## Datenmodell

```sql
CREATE TABLE kunde_sticker (
    kundennummer INTEGER NOT NULL,
    motiv        TEXT    NOT NULL,
    anzahl       INTEGER NOT NULL DEFAULT 1 CHECK (anzahl = 1),
    PRIMARY KEY (kundennummer, motiv),
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE CASCADE
);

ALTER TABLE kunde      ADD COLUMN starterset_erhalten   INTEGER NOT NULL DEFAULT 0;
ALTER TABLE bestellung ADD COLUMN starterset_ausgegeben INTEGER NOT NULL DEFAULT 0;
```

Das ist die **vierte Abweichung** vom Pflichtenheft (siehe
`docs/Architektur.md`, Kapitel 7). Ohne die Tabelle `kunde_sticker` weiß das
System nur, *wie viele* Sticker jemand hat, nicht *welche* — und dann gibt es
keine Sammlung.

`anzahl` ist seit der Einmaligkeitsregel immer 1. Der Primärschlüssel lässt
keine zweite Zeile zu, der `CHECK` keine zweite Gutschrift, und
`ON CONFLICT … DO NOTHING` beim Schreiben sorgt dafür, dass ein bereits
vorhandenes Motiv unverändert bleibt. Die Spalte bleibt trotzdem erhalten:
`SUM(anzahl)` ist damit weiterhin direkt mit `kunde.sticker_kontostand`
vergleichbar.

`ON DELETE CASCADE` sorgt dafür, dass das Album mit dem Kunden verschwindet
(/F43/). Das ist getestet: `test_album_verschwindet_mit_dem_kunden`.

## Ältere Datenbanken

`CREATE TABLE IF NOT EXISTS` legt bestehende Tabellen nicht neu an — neue
Spalten fehlen dort also. Wer die Anwendung schon benutzt hat, soll seine
`fanshop.db` aber nicht löschen müssen. `Datenbank._schema_nachziehen()`
ergänzt beim Start die fehlenden Spalten, setzt jede `kunde_sticker.anzahl` auf
1 und gleicht `sticker_kontostand` an die Zahl der Albumzeilen an. Ein zweiter
Start ändert dann nichts mehr. Geprüft in
`tests/test_datenbank.py::SchemaNachziehenTest`.

## Zwei Stände, die zusammenpassen müssen

`kunde.sticker_kontostand` (Zähler, aus dem Pflichtenheft) und die Summe über
`kunde_sticker.anzahl` (Album) sind zwei Darstellungen derselben Sache. Beide
werden in **derselben Transaktion** geschrieben — `kauf_verbuchen()` erhöht den
Zähler um genau so viele Sticker, wie es Motivzeilen schreibt, im selben
`with`-Block.

Der Test `test_zaehler_und_album_bleiben_gleich` prüft das nach fünf Einkäufen
— also auch nach den zweien, die gar keine Sticker mehr bringen.

## In der Oberfläche

* **Kasse, Schritt 1:** Beim Kunden stehen Anschrift, „4 von 6 Sammelstickern"
  und, wenn zutreffend, „Starterset erhalten".
* **Kasse, Schritt 4:** Vor dem Buchen steht dort, wie viele Sticker gleich
  herausgehen — und ob dieser Kauf das Starterset auslöst.
* **Nach dem Kauf:** Der Dialog zeigt die Motive als Bilder mit Titel und
  darunter „Sammlung: 4 von 6 Motiven". Liegt das Starterset bei, steht der
  Hinweis darunter. Ist die Sammlung schon voll, sagt der Dialog das ebenfalls,
  statt zwei Bilder zu erfinden.
* **Kundenkartei:** Alle sechs Motive nebeneinander — vorhandene in Farbe,
  fehlende grau und aufgehellt (`bild_laden(..., blass=True)`), darunter je ein
  Haken oder ein Strich. Eine Stückzahl wäre sinnlos, weil es jedes Motiv nur
  einmal gibt. Darunter der Starterset-Stand: erhalten, oder wie viele Einkäufe
  noch fehlen.
* **Sortiment:** Unter der Sonderaktionstabelle steht das Starterset als
  dauerhaftes Sonderangebot — mit Inhalt, Bedingung und dem Hinweis, dass es
  ohne Mindestbestellwert automatisch läuft.
* **Laufkundschaft** bekommt weder Sticker noch Album noch Starterset.

## Testdaten

`fanshop/datenbank/testdaten.py` füllt die Alben der Beispielbestellungen mit
**derselben** Funktion `offene_motive()`, die auch ein echter Kauf benutzt, und
prüft den Starterset-Anspruch mit derselben Regel. Sonst hätten die Testkunden
einen Zähler, aber ein leeres Album — und die Kartei sähe beim ersten Start
kaputt aus.

Die erste Kundin hat drei Beispielbestellungen. Damit ist beim allerersten
Start ein vollständiges Album samt vergebenem Sonderangebot zu sehen.
