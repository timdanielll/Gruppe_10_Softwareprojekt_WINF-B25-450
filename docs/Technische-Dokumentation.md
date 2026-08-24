# Technische Dokumentation — WI Fanshop

Projekt WINF-B25-450, Gruppe 10 · Stand: August 2026

Dieses Dokument beantwortet zwei Fragen:

1. **Was steckt in welcher Datei?** (Kapitel 2 und 3)
2. **Wo ist Anforderung X umgesetzt?** (Kapitel 4 — die Nachweistabelle)

Wie die Software aufgebaut ist und warum, steht in
[Architektur.md](Architektur.md).

---

## 1. Konventionen im Quellcode

Damit man beim Lesen nicht raten muss:

| Regel | Beispiel |
|---|---|
| Fachbegriffe sind **deutsch** — genau wie im Pflichtenheft | `Artikel`, `warenkorb.hinzufuegen()`, `kunden_repository.suchen()` |
| Technische Muster bleiben **englisch** | `Repository`, `Service` |
| Ein führender Unterstrich heißt „nur intern" | `KassenService._bestand_erneut_pruefen()` |
| Anforderungs-IDs stehen im Docstring | `"""… den Bestellwert (/F13/)."""` |
| Kommentare sind umlautfrei geschrieben | `Groesse`, `koennen` |
| Texte für den Benutzer haben echte Umlaute | `"Bitte einen Titel eingeben."` |

Der letzte Punkt ist Absicht: Kommentare sehen so in jedem Editor und jeder
Konsole gleich aus, während Fehlermeldungen und Beschriftungen dem Bediener
korrekt angezeigt werden.

---

## 2. Dateiübersicht

### 2.1 Start und Grundlagen

| Datei | Zeilen | Inhalt |
|---|---|---|
| `main.py` | 35 | Startpunkt: Design laden → `Anwendung` bauen → Fenster mit Rollenauswahl öffnen |
| `fanshop/konfiguration.py` | 67 | Pfade, die sieben Kategorien, Größen, Rabattsätze, Stickeranzahl, Starterset |
| `fanshop/fehler.py` | 29 | `FanshopFehler` und die drei Unterklassen |
| `fanshop/hilfsmittel.py` | 109 | `euro()`, `prozent()`, Datumsumwandlung, `zahl_aus_text()` |
| `fanshop/zugriff.py` | 14 | erlaubte Seitenschlüssel für `kunde` und `kassierer`; ohne GUI testbar |

`hilfsmittel.euro(1234.5)` liefert `"1.234,50 €"` — deutsches Format mit Komma
und Tausenderpunkt. `zahl_aus_text()` akzeptiert `"19,90"` **und** `"19.90"`,
weil Kassenpersonal beides tippt.

### 2.2 Datenbankschicht

| Datei | Zeilen | Inhalt |
|---|---|---|
| `fanshop/datenbank/schema.sql` | 110 | alle `CREATE TABLE`-Anweisungen und Indizes |
| `fanshop/datenbank/verbindung.py` | 112 | Klasse `Datenbank`, `datenbank_vorbereiten()` |
| `fanshop/datenbank/testdaten.py` | 253 | Beispielshop für den ersten Start |

Die Klasse `Datenbank` ist die einzige Stelle, die `sqlite3` direkt benutzt. Sie
bietet fünf Methoden:

```python
datenbank.abfragen(sql, parameter)        # SELECT → Liste von Zeilen
datenbank.abfragen_eine(sql, parameter)   # SELECT → erste Zeile oder None
datenbank.ausfuehren(sql, parameter)      # INSERT/UPDATE/DELETE → ID
datenbank.ausfuehren_viele(sql, liste)    # dieselbe Anweisung, viele Datensätze
with datenbank.transaktion() as verb: ... # alles oder nichts (/NF30/)
```

### 2.3 Fachklassen (`fanshop/modelle/`)

| Datei | Klassen | Besonderheit |
|---|---|---|
| `artikel.py` | `Artikel`, `Kleidungsartikel` | Vererbung + Fabrikmethode `aus_zeile()`; `groessen` kommt aus der Kategorie |
| `kunde.py` | `Kunde` | `darf_newsletter_rabatt_nutzen` |
| `bestellung.py` | `Bestellung`, `Bestellposition` | `kunde_anzeige` fängt gelöschte Kunden ab |
| `retoure.py` | `Retoure` | — |
| `sonderaktion.py` | `Sonderaktion` | zwei Arten: `kategorie`, `mindestwert` |
| `sticker.py` | `Stickermotiv`, `MOTIVE` | sechs Sammelmotive, zwei pro Kauf, reihum und jedes nur einmal (/F53/) |
| `starterset.py` | `INHALT`, `anspruch_besteht()` | das Sonderangebot: Stift, Block, Jutebeutel ab drei Einkäufen mit voller Sammlung (/F53/) |
| `warenkorb.py` | `Warenkorb`, `WarenkorbPosition`, `Preisuebersicht` | **die gesamte Rabattrechnung** |

Jede Klasse hat dasselbe Umwandlungspaar:
`aus_zeile(zeile)` (Datenbank → Objekt) und `als_datenbankwerte()`
(Objekt → Tupel für das `INSERT`).

### 2.4 Datenzugriff (`fanshop/repositories/`)

| Datei | Tabelle | Wichtigste Methoden |
|---|---|---|
| `basis_repository.py` | — | `anzahl`, `existiert`, `loeschen` |
| `artikel_repository.py` | `artikel` | `speichern`, `suchen`, `deaktivieren`, `umsatzstaerkste`, `haeufigste` |
| `kunden_repository.py` | `kunde` | `speichern`, `suchen`, `loeschen_und_anonymisieren`, `newsletter_setzen` |
| `bestell_repository.py` | 3 Tabellen | `kauf_verbuchen`, `retoure_verbuchen`, `positionen_zu`, `bereits_retourniert`, `anzahl_bestellungen` |
| (in `kunden_repository.py`) | `kunde_sticker` | `sticker_album`, `starterset_erhalten` |
| `bericht_repository.py` | Auswertungen | `kennzahlen`, `umsatzanteile`, `umsatz_je_kategorie` |
| `sonderaktion_repository.py` | `sonderaktion` | `aktive`, `aktivieren` |

### 2.5 Geschäftslogik (`fanshop/logik/`)

| Datei | Klasse | Zuständig für |
|---|---|---|
| `anwendung.py` | `Anwendung` | steckt alle Schichten zusammen |
| `artikel_service.py` | `ArtikelService` | Sortiment: prüfen, anlegen, pflegen, suchen |
| `kunden_service.py` | `KundenService`, `StartersetStand` | Kartei, Newsletter, Sammel- und Starterset-Stand |
| `kassen_service.py` | `KassenService`, `Kaufbeleg` | der Kassiervorgang |
| `retouren_service.py` | `RetourenService` | Rückgaben |
| `bericht_service.py` | `BerichtService`, `Bericht` | Auswertungen und Zeiträume |
| `sonderaktion_service.py` | `SonderaktionService` | Spezialangebote starten und beenden |

### 2.6 Oberfläche (`fanshop/gui/`)

| Datei | Zeilen | Inhalt |
|---|---|---|
| `design.py` | 250 | Farben, Schriften, Abstände, Logowahl (aus `DESIGN.md`) |
| `htw_saar_theme.json` | — | dieselben Werte im CustomTkinter-Format |
| `bausteine.py` | 1088 | `Panel`, `Feld`, `Tabelle`, `Dialog`, `Schrittleiste`, `Statuszeile`, `Bildkarte`, `Kachel`, `StickerAlbum`, `HtwBalken`, Knöpfe |
| `basis_seite.py` | 96 | `BasisSeite` — Basisklasse, Statuszeile, `melden()` |
| `app.py` | 258 | Rollenauswahl, rollenabhängiger Seitenaufbau, Navigation, Logo je Modus, Hell/Dunkel |
| `seite_kasse.py` | 764 | Kasse als Wizard mit vier Schritten |
| `seite_artikel.py` | 470 | Sortiment, Produktfoto-Auswahl, Sonderaktionen, Hinweis auf das dauerhafte Starterset-Sonderangebot |
| `seite_kunden.py` | 322 | Kunden |
| `seite_retouren.py` | 274 | Retouren |
| `seite_berichte.py` | 352 | Berichte |

---

## 3. Die wichtigsten Abläufe im Detail

### 3.1 Zugangsart auswählen

Beim Start baut `FanshopApp` zunächst nur die Auswahl „Als Kunde fortfahren“
oder „Als Kassierer fortfahren“. Erst beim Klick ruft
`app._rolle_waehlen()` die Funktion `zugriff.erlaubte_seiten()` auf und erzeugt
die erlaubten Navigationseinträge und Fachseiten:

```
Kunde       → Kasse
Kassierer   → Kasse, Sortiment, Kunden, Retouren, Berichte
```

Die Verwaltungsseiten werden im Kundenzugang nicht versteckt, sondern nicht
instanziiert. `test_rollenzugriff.py` prüft die Zuordnung ohne eine
GUI-Bibliothek. Die Wahl ist kein Login und schützt nicht mit Passwort; sie
legt nur den sichtbaren Funktionsumfang für diesen Programmstart fest.

### 3.2 Ein Artikel kommt in den Warenkorb (/F11/)

```
Bediener klickt „In den Warenkorb"
   │
   ▼  seite_kasse._artikel_uebernehmen()
       liest die markierte Zeile und das Mengenfeld
   │
   ▼  kassen_service.artikel_hinzufuegen(artikel_id, menge)
       lädt den Artikel FRISCH aus der Datenbank
       prüft: gibt es ihn? ist er aktiv?
   │
   ▼  warenkorb.hinzufuegen(artikel, menge)
       prüft: Menge ≥ 1? Lagerbestand ausreichend — auch kumuliert?
       legt an oder erhöht die vorhandene Position
   │
   ▼  seite_kasse._korb_anzeigen()
       zeichnet Tabelle und Summen neu
```

Warum wird der Artikel neu geladen? Weil der Lagerbestand sich seit dem Aufbau
der Liste geändert haben kann — etwa durch eine Retoure am anderen Ende des
Programms.

### 3.3 Der Bestellwert wird berechnet (/F13/)

`Warenkorb.berechne(sonderaktion, newsletter_rabatt_anwenden)` gibt eine
`Preisuebersicht` zurück:

| Feld | Bedeutung |
|---|---|
| `listenwert` | Summe aller Originalpreise, ohne jeden Rabatt |
| `artikelrabatt` | Summe der artikeleigenen Rabatte |
| `aktionsrabatt` | Rabatt der aktiven Sonderaktion |
| `newsletter_rabatt` | 10 % Willkommensrabatt (/F52/) |
| `zwischensumme` | `listenwert − artikelrabatt` |
| `gesamtbetrag` | was der Kunde zahlt |

Rechenbeispiel (steht so auch als Test in
`tests/test_warenkorb.py::test_alle_drei_rabatte_kumulieren_in_fester_reihenfolge`):

```
Rucksack, 100,00 €, Artikelrabatt 20 %, Aktion „10 % auf Accessoires",
Kunde hat Newsletter-Gutschein:

  100,00      Listenwert
 −  20,00     Artikelrabatt (20 %)
 =  80,00     Zwischensumme
 −   8,00     Sonderaktion (10 % von 80,00)
 =  72,00
 −   7,20     Newsletter (10 % von 72,00)
 =  64,80     Gesamtbetrag
```

### 3.4 Der Kauf wird abgeschlossen (/F14/)

```
kassen_service.kauf_abschliessen()
   ├── 1. Warenkorb leer?                   → ValidierungsFehler
   ├── 2. _bestand_erneut_pruefen()         → BestandsFehler
   ├── 3. preisuebersicht()                 → Preisuebersicht
   ├── 4. _praemien_bestimmen()             → bis zu 2 fehlende Motive (/F53/)
   │        • sticker.offene_motive(album)   → nie ein Motiv doppelt
   │        • starterset.anspruch_besteht()  → Set fällig? (3 Käufe + volles Album)
   ├── 5. bestell_repository.kauf_verbuchen()  ← EINE Transaktion:
   │        • INSERT bestellung (mit sticker_ausgegeben, starterset_ausgegeben)
   │        • INSERT bestellposition (je Position, mit gewaehlter Groesse)
   │        • UPDATE artikel  SET lagerbestand = lagerbestand − menge
   │        • UPDATE kunde    SET sticker_kontostand = … + Zahl der Motive
   │        • INSERT kunde_sticker (je Motiv, ON CONFLICT → DO NOTHING)
   │        • UPDATE kunde    SET starterset_erhalten = 1  (nur wenn noch 0)
   │        • UPDATE kunde    SET newsletter_rabatt_verfuegbar = 0
   ├── 6. Warenkorb leeren, Gutschein-Haken zurücksetzen
   └── 7. Kaufbeleg zurückgeben (Bestellnummer, Summen, Motive, Albumstand,
          Starterset)
```

Danach zeigt die GUI den Sticker-Dialog: die **zwei Motive** als Bilder mit
Titel und darunter „Sammlung: 4 von 6 Motiven". Ist die Sammlung damit voll,
steht der Hinweis auf das **Starterset** (Stift, Block, Jutebeutel) mit dabei.
Warum zwei verschiedene, jedes nur einmal, und warum das Set keine schaltbare
Sonderaktion ist — siehe [`../specs/09-sticker.md`](../specs/09-sticker.md).

### 3.5 Eine Retoure wird gebucht (/F51/)

```
retouren_service.retoure_buchen(bestellnummer, artikel_id, menge)
   ├── Menge ≥ 1?
   ├── Bestellung vorhanden?                → NichtGefundenFehler
   ├── War der Artikel in dieser Bestellung? → ValidierungsFehler
   ├── Noch offen? (gekauft − bereits retourniert)
   └── bestell_repository.retoure_verbuchen()   ← EINE Transaktion:
            • INSERT retoure
            • UPDATE artikel SET lagerbestand = lagerbestand + menge
```

Erstattet wird `menge × historischer_preis` — der Preis vom Kauftag. Ein
zwischenzeitlich geänderter Verkaufspreis spielt keine Rolle.

### 3.6 Ein Bericht entsteht (/F31/)

```
Schnellwahl-Knopf         →  bericht_service.zeitraum_schnellwahl("woche")
oder zwei Datumsfelder    →  bericht_service.zeitraum_aus_datum(von, bis)
                                 │ beide liefern (von_zeitstempel, bis_zeitstempel)
                                 ▼
                          bericht_service.bericht_erstellen(von, bis)
                                 ├── kennzahlen()         /F311/, /F312/
                                 ├── umsatzanteile()      /F313/
                                 └── umsatz_je_kategorie() für das Diagramm
```

Beim Enddatum zählt der **ganze Tag** mit (bis 23:59:59) — sonst bliebe ein
Bericht „vom 1. bis 1. August" leer.

---

## 4. Nachweistabelle: jede Anforderung und ihre Fundstelle

### 4.1 Funktionsgruppe 10 — Warenkorb und Kassiervorgang

| ID | Kriterium | Umgesetzt in | Test |
|---|---|---|---|
| /F11/ | Artikel hinzufügen | `KassenService.artikel_hinzufuegen()` → `Warenkorb.hinzufuegen()`; GUI: `seite_kasse._artikel_uebernehmen()` | `test_warenkorb.py` |
| /F12/ | Artikel entfernen | `Warenkorb.entfernen()`, `Warenkorb.menge_setzen()`; GUI: Knöpfe „Entfernen" und „Menge ändern" | `test_warenkorb.py` |
| /F13/ | Bestellwert berechnen | `Warenkorb.berechne()` → `Preisuebersicht` | `test_warenkorb.py` |
| /F14/ | Warenkorb bestellen | `KassenService.kauf_abschliessen()` → `BestellRepository.kauf_verbuchen()` | `test_kasse.py` |

### 4.2 Funktionsgruppe 20 — Artikelverwaltung

| ID | Kriterium | Umgesetzt in | Test |
|---|---|---|---|
| /F21/ | Artikel erstellen | `ArtikelService.anlegen()` inkl. `bildauswahl()` für das Produktfoto; GUI: `seite_artikel._anlegen()` | `test_artikel_und_kunden.py` |
| /F22/ | Artikel pflegen | `ArtikelService.aktualisieren()`, `bestand_setzen()`, `deaktivieren()` | `test_artikel_und_kunden.py` |
| /F23/ | Artikelsuche und Filter | `ArtikelRepository.suchen()` | `test_artikel_und_kunden.py` |
| /F231/ | … nach Kategorie | Parameter `kategorie` | ✓ |
| /F232/ | … nach Preisspanne | Parameter `min_preis`, `max_preis` | ✓ |
| /F233/ | … Volltext in Titel und Beschreibung | Parameter `suchtext` | ✓ |
| /F24/ | Umsatzstärkste Artikel | `ArtikelRepository.umsatzstaerkste()`; GUI: Seite Berichte | `test_retouren_und_berichte.py` |
| /F25/ | Häufigkeitsanalyse | `ArtikelRepository.haeufigste()`; GUI: Seite Berichte | `test_retouren_und_berichte.py` |
| /F26/ | Grafik Umsatz *(Kann)* | `seite_berichte._diagramm_umsatz()` (matplotlib) | manuell |
| /F27/ | Grafik Häufigkeit *(Kann)* | `seite_berichte._diagramm_haeufigkeit()` | manuell |

### 4.3 Funktionsgruppe 30 — Berichte und Controlling

| ID | Kriterium | Umgesetzt in | Test |
|---|---|---|---|
| /F31/ | Zeitraumbezogene Berichte | `BerichtService.zeitraum_schnellwahl()`, `zeitraum_aus_datum()`, `bericht_erstellen()` | `test_retouren_und_berichte.py` |
| /F311/ | Bestellungszähler | `BerichtRepository.kennzahlen()` → `anzahl_bestellungen` | ✓ |
| /F312/ | Umsatzausgabe | `BerichtRepository.kennzahlen()` → `umsatz` | ✓ |
| /F313/ | Umsatzanteile prozentual | `BerichtRepository.umsatzanteile()` | ✓ |

### 4.4 Funktionsgruppe 40 — Kundenverwaltung

| ID | Kriterium | Umgesetzt in | Test |
|---|---|---|---|
| /F41/ | Kunden auflisten | `KundenService.alle()`; GUI: Tabelle auf der Seite Kunden | `test_artikel_und_kunden.py` |
| /F42/ | Kunden hinzufügen | `KundenService.anlegen()` (Kundennummer vergibt die Datenbank) | ✓ |
| /F43/ | Kunden löschen | `KundenRepository.loeschen_und_anonymisieren()` | ✓ |
| /F44/ | Kunden suchen | `KundenRepository.suchen()` (Name **oder** Kundennummer) | ✓ |

### 4.5 Funktionsgruppe 50 — Erweiterungsmodule

| ID | Kriterium | Umgesetzt in | Test |
|---|---|---|---|
| /F51/ | Retourenabwicklung | `RetourenService`, `BestellRepository.retoure_verbuchen()` | `test_retouren_und_berichte.py` |
| /F52/ | Newsletter und Rabatt | `KundenRepository.newsletter_setzen()`, `Warenkorb.berechne()` | `test_kasse.py` |
| /F53/ | Sticker-Sammelsystem *(Kann)* | `modelle/sticker.py`, `modelle/starterset.py`, Tabelle `kunde_sticker`, Spalten `kunde.starterset_erhalten` / `bestellung.starterset_ausgegeben`, `kauf_verbuchen()`; GUI: Sticker-Dialog mit Starterset-Hinweis, Album und Starterset-Stand in der Kartei, Dauerangebot im Sortiment | `test_sticker.py`, `test_starterset.py` |
| /F54/ | Dark-Mode *(Kann)* | `design.modus_umschalten()`, `app._modus_gewaehlt()`; eigener Akzent und eigenes Logo je Modus | manuell |

### 4.6 Nicht-funktionale Anforderungen

| ID | Anforderung | Wie erfüllt |
|---|---|---|
| /NF10/ | vollständig grafische Bedienung | Nach der grafischen Rollenauswahl liegen alle für die gewählte Zugangsart erlaubten Funktionen auf Fachseiten. Die Konsole gibt nur beim allerersten Start eine Zeile aus. |
| /NF11/ | verständliche Fehlerdialoge | `FanshopFehler` mit deutschem Text → `bausteine.fehler_zeigen()`; zusätzlich rote Zeile unter dem betroffenen Feld und ein Eintrag in der Statuszeile |
| /NF12/ | linearer Kassenablauf | Die Seite Kasse ist eine **Strecke aus vier Schritten** mit „Zurück" und „Weiter": 1. Kunde, 2. Artikel, 3. Warenkorb und Rabatte, 4. Abschluss. Pro Schritt steht nur, was dort gebraucht wird. |
| /NF20/ | objektorientiertes Design | drei Vererbungshierarchien (siehe Architektur, Kapitel 4), Kapselung über `_`-Methoden, Fabrikmethode `Artikel.aus_zeile()` |
| /NF21/ | Trennung Frontend/Backend | vier Schichten, Aufrufrichtung nur nach unten; alle 177 Tests laufen ohne GUI |
| /NF30/ | keine korrupten Daten | `PRAGMA foreign_keys = ON`, `Datenbank.transaktion()`, Kauf und Retoure jeweils als eine Transaktion |

---

## 5. Testfälle zum Durchklicken

Die automatischen Tests decken die Logik ab. Die Oberfläche prüft man einmal von
Hand — diese Liste dauert etwa zehn Minuten.

| # | Was tun | Erwartet |
|---|---|---|
| 1 | `python main.py` beim ersten Mal | Fenster zeigt zuerst die Auswahl „Als Kunde fortfahren“ und „Als Kassierer fortfahren“ |
| 1a | **Als Kunde fortfahren** | Es öffnet sich die Kasse auf Schritt 1 „Kunde“; die Navigation enthält nur „Kasse“ |
| 1b | Programm schließen, erneut starten, **Als Kassierer fortfahren** | Kasse öffnet sich auf Schritt 1 mit 5 Kunden in der Liste; die Navigation enthält alle fünf Fachseiten |
| 2 | Kunde „Anna Becker" anklicken | Rechts erscheinen Anschrift, Stickerstand und der Gutschein-Hinweis; unten meldet die Statuszeile „Anna Becker ausgewählt." |
| 3 | **Weiter** | Schritt 2 „Artikel", Schritt 1 ist golden umrandet |
| 4 | Suchfeld: `htw` tippen | Liste wird beim Tippen kürzer, ohne Ruckeln |
| 5 | Eine Zeile anklicken | Rechts erscheinen Produktfoto, Kategorie, Preis und Bestand; bei Kleidung füllt sich die Größenliste |
| 6 | Kategorie „Schreibwaren" wählen | Nur Schreibwaren, Suchtext bleibt wirksam |
| 7 | Preis ab `100`, Preis bis `10`, **Filtern** | Dialog: „Der Mindestpreis darf nicht größer …" |
| 8 | **Zurücksetzen** | Alle Filter leer, volle Liste |
| 9 | Menge `999`, **In den Warenkorb** | Dialog: „… sind nur noch N Stück auf Lager" |
| 9b | Einen Herren-Hoodie markieren | Größenliste zeigt S bis 5XL; bei einer Tasse ist das Feld gesperrt |
| 9c | Größe „5XL" wählen, **In den Warenkorb** | Statuszeile meldet „1 × … (Gr. 5XL)" |
| 9d | Denselben Hoodie in „M" dazulegen | Der Warenkorb zeigt **zwei** Zeilen mit verschiedenen Größen |
| 10 | Artikel doppelklicken | Liegt im Korb; Statuszeile meldet es, oben rechts steht der neue Korbstand |
| 11 | **Weiter** | Schritt 3 „Warenkorb" mit allen Positionen |
| 12 | Haken „Newsletter-Rabatt" setzen | Eine weitere Rabattzeile, „Zu zahlen" sinkt um 10 % |
| 13 | Zeile wählen, Menge `3`, **Menge setzen** | Menge und Summen ändern sich |
| 14 | **Weiter** | Schritt 4 „Abschluss" mit fertigem Beleg |
| 14b | Oben in der Strecke auf „2 Artikel" klicken | Springt zurück; von dort direkt auf „4 Abschluss" klicken springt vorwärts |
| 15 | **Kauf abschließen** | Dialog mit **zwei verschiedenen** Stickerbildern und „Sammlung: 2 von 6 Motiven" |
| 16 | Zurück auf Schritt 1 | Die Kasse steht wieder am Anfang, Korb ist leer |
| 17 | Seite Kunden → den eben bedienten Kunden | Sammelstand „2 / 6", im Album zwei Motive farbig, vier blass; darunter „noch 2 Einkäufe bis zur vollen Sammlung" |
| 18 | Zweimal weiter kaufen, dann Kartei prüfen | Album zeigt „6 von 6 Motiven"; der Kaufdialog nennt beim dritten Mal das **Starterset**, die Kartei meldet „Starterset erhalten: Stift, Block und Jutebeutel." |
| 18b | Ein viertes Mal kaufen | Dialog meldet, dass alle Motive schon da sind — **keine** neuen Sticker, **kein** zweites Set |
| 19 | Seite Sortiment → gekaufter Artikel | Lagerbestand um die gekaufte Menge kleiner, Foto in der Maske |
| 19b | **Neu** drücken | Maske leer, Bildfläche zeigt „kein Foto" — **nicht** das Foto des vorher gewählten Artikels |
| 19c | Unter „Produktfoto" ein Bild wählen | Foto erscheint sofort in der Karte und wird beim Anlegen gespeichert |
| 19d | Im Formular nach unten scrollen | „Artikel anlegen", „Speichern", „Neu" und „Deaktivieren" bleiben unten stehen und sind immer klickbar |
| 19e | Fenster schmaler ziehen | Spalten werden enger, aber **keine** verschwindet; alle Überschriften bleiben lesbar |
| 19f | Seite Kunden, im Formular scrollen | „Kunde anlegen", „Änderungen speichern", „Neu" und „Kunde löschen" bleiben sichtbar |
| 20 | Artikel ohne Titel anlegen | Dialog: „Bitte einen Titel für den Artikel eingeben." |
| 21 | Artikel anlegen, Preis `12,50` | Erscheint sofort in der Liste und in der Kasse |
| 22 | **Deaktivieren** | Sicherheitsabfrage; danach verschwindet er aus der Kasse |
| 23 | Haken „Deaktivierte mit anzeigen" | Er taucht mit Status „deaktiviert" wieder auf |
| 24 | Sortiment → Sonderaktion wählen, **Aktion starten** | Status springt auf „aktiv"; in der Kasse erscheint sie in Schritt 3 |
| 24b | Unter der Aktionstabelle nachsehen | Der Hinweis auf das dauerhafte Starterset-Sonderangebot bleibt sichtbar — er wird von keiner Aktion abgelöst |
| 25 | **Alle beenden** | Kein „aktiv" mehr; die Rabattzeile verschwindet aus der Kasse |
| 26 | Retouren: Bestellnummer aus Schritt 15 eingeben | Positionen der Bestellung erscheinen |
| 27 | Position wählen, Menge 1, **Retoure buchen** | Dialog mit Erstattungsbetrag samt Größe; „Offen" sinkt um 1 |
| 27b | Bei zwei Größen desselben Artikels die eine ganz zurückgeben | Nur diese Zeile wird grau — die andere Größe bleibt offen |
| 28 | Dieselbe Position über die Menge hinaus | Dialog: „Es können nur noch N Stück …" |
| 28b | Position vollständig zurückgeben | Zeile wird grau und zeigt „zurück" statt 0 |
| 28c | Auf die graue Zeile klicken und buchen | Nur eine Zeile in der Statusleiste, **kein** Dialog |
| 29 | Berichte → **Gesamthistorie** | Bestellungen, Umsatz, Erstattungen, Nettoumsatz gefüllt |
| 30 | Von `20.08.2026` eingeben | Dialog: „Bitte das Datum im Format JJJJ-MM-TT …" |
| 31 | **Umsatz je Kategorie** | Fenster mit goldenem Balkendiagramm; Escape schließt es |
| 32 | Kunden: Kunde löschen | Sicherheitsabfrage; danach steht in Retouren „Geloeschter Kunde" |
| 33 | Unten links auf das **Mondsymbol** | Alles wird dunkel, auch die Tabellen. Das Logo wechselt auf die goldene Fakultätsvariante, und **alle Akzente wechseln von htw-Blau auf WiWi-Gold** — Buttons, aktiver Navigationseintrag, aktueller Schritt, markierte Tabellenzeile |
| 34 | Programm schließen und neu starten | Alle Daten noch da, keine neuen Testdaten |

## 6. Häufige Fragen

**Die Anwendung startet nicht: `ModuleNotFoundError: No module named 'customtkinter'`**
`pip install -r requirements.txt` ausführen. Bei mehreren Python-Versionen:
`python -m pip install -r requirements.txt`.

**Schützt „Kassierer“ die Verwaltungsseiten mit einem Passwort?**
Nein. Die Auswahl steuert nur, welche Seiten für diesen Start aufgebaut werden.
Für einen geschützten Verwaltungszugang wären Benutzerkonten und eine
Anmeldung nötig; das Projekt enthält sie bewusst nicht.

**Ich möchte die Testdaten zurücksetzen.**
`fanshop.db` im Projektverzeichnis löschen und `python main.py` starten. Die
Datei steht in `.gitignore` und ist nie im Repository.

**Die Diagramme öffnen sich nicht.**
matplotlib fehlt. Die Anwendung sagt das im Dialog und läuft weiter — die
Diagramme sind Kann-Kriterien (/F26/, /F27/).

**Wo kommen die Artikel her?**
Aus `assets/artikel/katalog.json`. Die Datei ordnet jedem der 31 Produktfotos
Titel, Kategorie, Beschreibung und Preis zu — ohne Größe. Wer einen Artikel umbenennen
will, ändert die Datei und löscht `fanshop.db`.

**Stimmen die Preise?**
Ja — sie wurden mit dem echten htw-saar-Webshop abgeglichen (Kategorieseiten
Textilien, Accessoires, Schreibwaren, Print). Ein Schlüsselband kostet dort
1,95 €, eine Fleecejacke 32,50 €. Vier Artikel (Klappkarte, Briefpapier,
Kartenetui, Stiftemäppchen) gibt es im echten Shop nicht; ihre Preise sind
geschätzt.

**Warum steht die Größe nicht am Artikel?**
Weil sonst jedes Kleidungsstück so oft im Sortiment stünde, wie es Größen gibt —
ein Herren-Hoodie achtmal. Genau daher kam die doppelte Fleecejacke. Jetzt gibt
es jeden Artikel einmal; die Größe wird beim Bestellen gewählt und auf der
Bestellposition festgehalten. Welche Größen möglich sind, hängt an der Kategorie
(`GROESSEN_JE_KATEGORIE`): Damen S–XL, Herren S–5XL.

**Warum hängt die Retoure an der Position und nicht am Artikel?**
Weil derselbe Artikel seit der Größenwahl zweimal in einer Bestellung stehen
kann — ein Hoodie in M und einer in L. Würde die Retoure nur die Artikelnummer
kennen, würde eine Rückgabe beide Zeilen belasten. Deshalb trägt `retoure` eine
`position_id`.

**Gibt es getrennte Lagerbestände je Größe?**
Nein. Der Bestand wird je Artikel geführt: 10 Hoodies heißt 10 insgesamt. Für
einen Verkaufsstand mit einer Kiste hinter dem Tresen ist das die ehrlichere
Abbildung als ein Größenlager, das niemand pflegt.

**Warum bekommt ein Kunde zwei verschiedene Sticker und nicht zweimal denselben?**
Weil im Assets-Ordner sechs Motive liegen und aus einem Zähler sonst keine
Sammlung wird. Die Vergabe läuft reihum, nicht zufällig, und **jedes Motiv gibt
es nur ein einziges Mal** — nach drei Einkäufen ist das Album genau einmal
komplett, danach gibt es keine Sticker mehr. Begründung in
[`../specs/09-sticker.md`](../specs/09-sticker.md).

**Was ist das Starterset und warum steht es nicht in der Tabelle `sonderaktion`?**
Wer drei Einkäufe getätigt und alle sechs Motive gesammelt hat, bekommt einmalig
Stift, Block und Jutebeutel gratis — gutgeschrieben aufs Kundenkonto und der
Bestellung beigelegt. Eine `Sonderaktion` ist dagegen ein Rabattsatz, von dem
immer nur einer gleichzeitig laufen darf; das Starterset senkt keinen Preis und
soll durchgehend gelten. Es steht deshalb als eigene Fachregel in
`modelle/starterset.py` und erscheint im Sortiment als **dauerhaftes
Sonderangebot** unter der Aktionstabelle. Einen Mindestbestellwert gibt es
weder für die Sticker noch für das Set.

**Warum sind Preise manchmal `2,12 €` und nicht `2,50 €`?**
Der angezeigte Preis in der Kasse ist der **Endpreis** nach dem
artikeleigenen Rabatt. Den Originalpreis zeigt die Seite Sortiment.

**Wie bekommt ein neu angelegter Artikel ein Foto?**
Über die Auswahlliste „Produktfoto" in der Artikelmaske. Sie zeigt alle Bilder
aus `assets/artikel/`, beschriftet mit dem Titel des Artikels, der das Bild
bereits benutzt — ein Dateiname wie „WhatsApp Image 2026-08-20 …" sagt niemandem
etwas. Ein Hochladen eigener Dateien gibt es bewusst nicht; das Pflichtenheft
sieht keine Dateiverwaltung vor.

**Warum bekomme ich keine Meldung mehr, wenn etwas geklappt hat?**
Doch — sie steht unten in der Statuszeile. Dialoge öffnen sich nur noch bei
Fehlern, Sicherheitsabfragen und beim Kaufabschluss.

**Die Schrift sieht bei mir anders aus.**
`design.schriftfamilie()` nimmt die erste Schrift, die auf dem Rechner vorhanden
ist: Segoe UI (Windows), Helvetica Neue (macOS), DejaVu Sans (Linux). Für Zahlen
entsprechend Consolas / Menlo / DejaVu Sans Mono.

**Kann ich die Fenstergröße ändern?**
Ja, das Fenster ist frei skalierbar — aber nicht kleiner als 1280 × 800. Darunter
passen die Tabellen nicht mehr nebeneinander.
