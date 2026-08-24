# Architekturdokumentation — WI Fanshop

Projekt WINF-B25-450, Gruppe 10 · Stand: August 2026

Dieses Dokument erklärt, **wie** die Software aufgebaut ist und **warum** sie so
aufgebaut ist. Wer wissen will, in welcher Datei eine bestimmte Anforderung
steckt, findet das in [Technische-Dokumentation.md](Technische-Dokumentation.md).

---

## 1. Überblick

Der WI Fanshop ist eine lokale Desktop-Anwendung. Es gibt keinen Server, kein
Netzwerk und keine zweite Instanz. Alles läuft in einem einzigen Python-Prozess
und schreibt in eine einzige Datei.

```
        ┌─────────────────────────────────┐
        │ Kunde / Kassenpersonal / Leitung │
        └────────────────┬────────────────┘
                         │ Maus und Tastatur
        ┌────────────────▼────────────────┐
        │  WI Fanshop (ein Python-Prozess)│
        └────────────────┬────────────────┘
                         │ SQL
        ┌────────────────▼────────────────┐
        │  fanshop.db  (SQLite-Datei)     │
        └─────────────────────────────────┘
```

---

## 2. Die vier Schichten

Die zentrale Vorgabe aus dem Pflichtenheft ist /NF21/: „Konsequente
Separierung von Frontend und Backend. Die Programmlogik muss vollständig
unabhängig von den GUI-Klassen lauffähig und testbar sein."

Umgesetzt ist das als vier Schichten. **Jede Schicht kennt nur die Schicht
unter sich** — rückwärts gibt es keinen einzigen Import.

```
┌────────────────────────────────────────────────────────────┐
│  fanshop/gui/         Oberfläche (CustomTkinter)           │
│  Zeigt an und nimmt Klicks entgegen.                       │
│  Enthält: keine Rechnung, kein SQL.                        │
└───────────────────────────┬────────────────────────────────┘
                            │ ruft Services auf
┌───────────────────────────▼────────────────────────────────┐
│  fanshop/logik/       Geschäftslogik (Services)            │
│  Prüft Eingaben, rechnet, entscheidet.                     │
│  Enthält: keine Widgets, kein SQL.                         │
└───────────────────────────┬────────────────────────────────┘
                            │ ruft Repositories auf
┌───────────────────────────▼────────────────────────────────┐
│  fanshop/repositories/  Datenzugriff                       │
│  Der einzige Ort im Projekt, an dem SQL steht.             │
└───────────────────────────┬────────────────────────────────┘
                            │ benutzt
┌───────────────────────────▼────────────────────────────────┐
│  fanshop/datenbank/   SQLite-Verbindung und Schema         │
└────────────────────────────────────────────────────────────┘

    fanshop/modelle/   Fachklassen — werden von allen Schichten
                       gereicht, kennen aber selbst keine Schicht.
```

### Wie man die Regel prüft

Es braucht kein Werkzeug dafür — ein Blick in die Importzeilen genügt:

| In diesen Dateien darf **nicht** vorkommen | Suchbegriff |
|---|---|
| `fanshop/logik/*`, `fanshop/modelle/*` | `customtkinter` |
| `fanshop/gui/*` | `sqlite3`, `repositories` |
| `fanshop/modelle/*` | `sqlite3.connect` |

Der praktische Beweis sind die Tests: Alle 94 laufen ohne ein einziges Fenster.

---

## 3. Der Zusammenbau: die Klasse `Anwendung`

Damit nicht jedes Fenster selbst eine Datenbankverbindung aufmacht, gibt es
genau eine Stelle, an der alles zusammengesteckt wird —
`fanshop/logik/anwendung.py`:

```python
anwendung = Anwendung()          # Datenbank + 5 Repositories + 6 Services
fenster = FanshopApp(anwendung)  # die GUI bekommt dieses eine Objekt
```

Jede Seite der Oberfläche greift über `self.anwendung.artikel_service`,
`self.anwendung.kassen_service` usw. auf die Logik zu. Vorteile:

- Die Datenbankverbindung existiert genau einmal.
- Für einen Test genügt `Anwendung(datenbank_pfad=":memory:", testdaten=False)`
  — dieselbe Logik, andere Datenbank.
- Man sieht auf 73 Zeilen, woraus das Programm besteht.

### 3.1 Rollenauswahl und bedarfsgerechter Seitenaufbau

`FanshopApp` zeigt vor Navigation und Fachseiten eine Auswahl der Zugangsart.
Nach der Wahl fragt sie `fanshop/zugriff.py`, welche Seitenschlüssel erlaubt
sind, und baut ausschließlich diese Widgets:

| Zugangsart | Angelegte Seiten |
|---|---|
| `kunde` | `kasse` |
| `kassierer` | `kasse`, `artikel`, `kunden`, `retouren`, `berichte` |

Die Regel steht absichtlich außerhalb der GUI. So prüft
`tests/test_rollenzugriff.py` sie ohne CustomTkinter und ohne geöffnetes
Fenster. Das trennt die Entscheidung „welche Bereiche gehören zu dieser
Ansicht?“ vom Aufbau der Buttons und Seiten.

Die Wahl wird bei jedem Programmstart neu getroffen und ist keine Anmeldung:
Sie enthält weder Passwörter noch Benutzerkonten. Sie beschränkt den
Funktionsumfang der Oberfläche, ersetzt aber kein Berechtigungssystem.

---

## 4. Objektorientierung und Vererbung (/NF20/)

Es gibt drei Vererbungshierarchien. Keine davon ist gebaut worden, um eine
Anforderung abzuhaken — jede löst ein konkretes Problem.

### 4.1 `Artikel` → `Kleidungsartikel`

Das Lastenheft verlangt: „Artikel haben in Abhängigkeit ihrer Kategorie weitere
Merkmale (Herren / Damen, Größe etc.)".

```
Artikel                     titel, kategorie, preis, rabattsatz, lagerbestand …
  │                         groessen        → ()
  │                         merkmale()      → ""
  │                         groesse_pruefen() → ""
  └── Kleidungsartikel      groessen        → ("S", "M", "L", "XL", …)
                            merkmale()      → "Größen: S, M, L, XL"
                            groesse_pruefen("xl") → "XL", sonst Fehler
```

Die Größe ist dabei **kein Feld des Artikels**, sondern eine Spanne, die an der
Kategorie hängt (Damen S–XL, Herren S–5XL, siehe
`konfiguration.GROESSEN_JE_KATEGORIE`). Jedes Kleidungsstück steht genau einmal
im Sortiment; welche Größe der Kunde will, entscheidet sich beim Bestellen und
landet auf der Bestellposition. Damen und Herren führen deshalb dasselbe
Sortiment und unterscheiden sich nur in der Spanne.

Welche Klasse entsteht, entscheidet die **Fabrikmethode** `Artikel.aus_zeile()`
anhand der Kategorie. Die Oberfläche ruft immer nur `artikel.merkmale()` auf und
muss nie prüfen, welche Artikelart vorliegt — das ist Polymorphie im praktischen
Einsatz.

### 4.2 `BasisRepository` → fünf Repositories

Jedes Repository kennt seinen Tabellennamen und seinen Primärschlüssel und erbt
dadurch `anzahl()`, `existiert()` und `loeschen()` — Methoden, die sonst fünfmal
identisch dastünden.

### 4.3 `BasisSeite` → fünf GUI-Seiten

Alle Seiten haben denselben Aufbau (Titelzeile, Inhaltsbereich) und dieselben
drei Einstiegspunkte: `aufbauen()`, `beim_anzeigen()`, `stil_aktualisieren()`.
Wer eine Seite verstanden hat, versteht alle fünf.

---

## 5. Wichtige Entwurfsentscheidungen

### 5.1 Die Preisberechnung steht an genau einer Stelle

`Warenkorb.berechne()` in `fanshop/modelle/warenkorb.py` ist die **einzige**
Stelle im Projekt, an der Rabatte gerechnet werden. Die Reihenfolge ist fest:

```
Listenwert
  − Artikelrabatt        (artikel.rabattsatz, je Position)
  = Zwischensumme
  − Sonderaktion         (Kategorie-Rabatt oder Rabatt ab Mindestbestellwert)
  − Newsletter-Rabatt    (10 % auf den Rest, /F52/)
  = Gesamtbetrag
```

Warum diese Reihenfolge? Sie ist unabhängig davon, in welcher Reihenfolge die
Artikel in den Korb gelegt wurden, und der Kunde kann nie mehr als 100 % Rabatt
bekommen. Das Ergebnis ist ein `Preisuebersicht`-Objekt mit allen Einzelbeträgen
— die GUI beschriftet damit jede Zeile der Summenanzeige, ohne selbst zu rechnen.

### 5.2 Der gezahlte Preis wird auf die Positionen verteilt

Rabatte auf den ganzen Warenkorb (Sonderaktion, Newsletter) gelten rechnerisch
für den Gesamtbetrag. Gespeichert werden sie trotzdem **pro Position**:

```
faktor = gesamtbetrag / zwischensumme
historischer_preis = einzelpreis × faktor
```

Ohne diese Verteilung würde eine spätere Retoure mehr Geld erstatten, als der
Kunde je gezahlt hat. Das Pflichtenheft nennt `historischer_preis` ausdrücklich
den „tatsächlich gezahlten Einzelpreis" — genau das ist damit erfüllt.

### 5.3 Ein Kauf ist eine Transaktion

`BestellRepository.kauf_verbuchen()` schreibt in einem einzigen `with`-Block:
Bestellung, alle Positionen, Lagerabgang, Sticker-Gutschrift, die einmalige
Starterset-Gutschrift (/F53/) und den Verbrauch des Newsletter-Gutscheins.

Das ist bewusst **eine** Methode und nicht sechs Aufrufe. Bei fünf getrennten
Aufrufen könnte nach einem Absturz eine Bestellung existieren, deren Ware nie
aus dem Lager gebucht wurde. /NF30/ verlangt genau das Gegenteil: entweder alles
oder nichts.

Dasselbe gilt für `retoure_verbuchen()` (Beleg + Lagerzugang) und
`loeschen_und_anonymisieren()` (Bestellungen anonymisieren + Kunde löschen).

### 5.4 Artikel werden deaktiviert, Kunden gelöscht

- **Artikel:** Soft-Delete (`aktiv = 0`). Alte Bestellungen und Retouren
  verweisen auf den Artikel und müssen lesbar bleiben (/F22/).
- **Kunden:** echtes `DELETE`, aber die Bestellungen bekommen vorher
  `kundennummer = NULL` (/F43/). Der Umsatz bleibt damit in jedem Bericht
  erhalten, die Person ist aber nicht mehr zuzuordnen.

### 5.5 Fehler wandern als Ausnahme nach oben

Die Logikschicht öffnet nie ein Dialogfenster. Sie wirft einen Fehler mit einem
fertigen deutschen Text:

```
FanshopFehler
├── ValidierungsFehler    Eingabe unvollständig oder unplausibel
├── BestandsFehler        Lagerbestand reicht nicht (/F11/)
└── NichtGefundenFehler   Datensatz existiert nicht
```

Die GUI fängt nur `FanshopFehler` und zeigt `str(fehler)` im Pop-up (/NF11/).
Jeder Meldungstext steht damit genau **einmal** im Projekt — dort, wo das
Problem festgestellt wird.

### 5.6 Der Zustand einer Bedienung lebt im `KassenService`

Betriebsbedingung 2.3 des Pflichtenhefts: „Das Programm verarbeitet pro Sitzung
genau einen aktiven Kunden." Entsprechend hält der `KassenService` drei Dinge:
den aktiven Kunden, den Warenkorb und die Frage, ob der Newsletter-Gutschein
eingesetzt wird. Die GUI speichert davon nichts selbst — sie fragt bei jedem
Zeichnen nach.

---

## 6. Datenmodell

```
   kunde                          artikel
   ─────                          ───────
   kundennummer (PK)  ◄──┐        artikel_id (PK)
   name                  │        kategorie, titel, beschreibung
   strasse, plz, ort     │        preis, rabattsatz, lagerbestand
   newsletter_aktiv      │        erstellungsdatum, aktiv
   newsletter_rabatt_…   │        bildpfad
   sticker_kontostand    │              ▲          ▲
   starterset_erhalten   │              │          │
                         │              │          │
   bestellung            │              │          │
   ──────────            │              │          │
   bestellnummer (PK)    │              │          │
   kundennummer (FK) ────┘ NULL erlaubt │          │
   zeitstempel                          │          │
   gesamtbetrag                         │          │
   newsletter_rabatt_angewendet         │          │
   sticker_ausgegeben                   │          │
   starterset_ausgegeben                │          │
      ▲            ▲                    │          │
      │            │                    │          │
   bestellposition │                 retoure       │
   ───────────────  │                 ───────      │
   position_id (PK) │                 retouren_id (PK)
   bestellnummer (FK, ON DELETE CASCADE)
   artikel_id (FK) ─┘                 bestellnummer (FK)
   menge                              artikel_id (FK) ──┘
   historischer_preis                 menge
                                      retouren_datum
   sonderaktion                       erstattungsbetrag
   ────────────
   aktions_id (PK)
   titel, art, zielkategorie
   mindestbestellwert, rabattsatz, aktiv

   kunde_sticker
   ─────────────
   kundennummer (PK, FK, ON DELETE CASCADE)
   motiv        (PK)  Schluessel aus modelle/sticker.py
   anzahl             immer 1 - jedes Motiv gibt es nur einmal
```

**Stammdaten:** `kunde`, `artikel`, `sonderaktion`
**Bewegungsdaten:** `bestellung`, `bestellposition`, `retoure`

Diese Trennung verlangt das Lastenheft ausdrücklich.

### Zwei Feinheiten

- `bestellung.kundennummer` darf `NULL` sein — das ist die Anonymisierung
  gelöschter Kunden (/F43/).
- `bestellposition` hängt mit `ON DELETE CASCADE` an der Bestellung: Wird ein
  Beleg gelöscht, verschwinden seine Zeilen mit. Bestellungen werden im Betrieb
  allerdings nie gelöscht.

---

## 7. Abweichungen vom Pflichtenheft

Fünf Punkte gehen über Kapitel 6 des Pflichtenhefts hinaus. Alle sind
Ergänzungen — es wurde nichts weggelassen.

| Abweichung | Warum |
|---|---|
| Spalte `bestellposition.groesse` | Das Lastenheft verlangt kategorieabhängige Merkmale („Herren / Damen, Größe etc."). Die Größe steht dabei **nicht** am Artikel: Jedes Kleidungsstück gibt es genau einmal und in allen Größen seiner Kategorie, gewählt wird beim Bestellen. Ohne diese Spalte wüsste die Bestellung nicht, welche Größe über den Tresen ging. |
| Spalte `artikel.bildpfad` | Verweist auf das Produktfoto in `assets/artikel/`. Das Pflichtenheft nennt die Produktbilder des htw-saar-Webshops als Quelle, sieht aber kein Feld dafür vor. |
| Tabelle `sonderaktion` | Das Lastenheft fordert „fest definierte Spezialangebote, die aktiviert werden können". Ohne Tabelle würde der Aktivierungsstatus einen Programmneustart nicht überleben. |
| Tabelle `kunde_sticker` | Das Pflichtenheft zählt Sticker nur (`sticker_kontostand`). Im Assets-Ordner liegen aber sechs verschiedene Motive. Ohne diese Tabelle weiß das System nicht, *welche* ein Kunde besitzt — und /F53/ wäre ein Zähler statt einer Sammlung. Details in [`../specs/09-sticker.md`](../specs/09-sticker.md). |
| Spalten `kunde.starterset_erhalten` und `bestellung.starterset_ausgegeben` | Das Starterset-Sonderangebot (Stift, Block, Jutebeutel ab drei Einkäufen mit voller Sammlung) gibt es **einmal je Kunde**. Ohne diese Flags ließe sich weder die Sperre durchsetzen noch nachvollziehen, welcher Bestellung das Set beilag. Details in [`../specs/09-sticker.md`](../specs/09-sticker.md). |

Zusätzlich weist der Bericht neben dem geforderten Umsatz (/F312/) auch
**Erstattungen** und **Nettoumsatz** aus. Ein Bericht, der nur den Bruttoumsatz
zeigt, verschweigt der Shop-Leitung das zurückgezahlte Geld.

Eine Einordnung, die keine Abweichung ist: Die Auswertungen /F24/ und /F25/
stehen im Pflichtenheft unter „Artikelverwaltung", in der Oberfläche liegen sie
aber auf der Seite **Berichte**. Sie sind Auswertungen und gehören zu den
anderen Auswertungen; die Funktion selbst ist unverändert.

---

## 8. Designsystem

Das Aussehen ist nicht improvisiert, sondern in [`../DESIGN.md`](../DESIGN.md)
festgelegt — im DESIGN.md-Format von Google, geprüft mit dessen Linter
(0 Fehler, 0 Warnungen).

Die Farben stammen aus dem Corporate Design der htw saar:

| Farbe | Wert | Herkunft |
|---|---|---|
| htw-Blau, aufgehellt | `#4CC2EE` | Vierfarbbalken-Blau +30 % — Akzent im **Hellmodus** |
| WiWi-Gold | `#F7A823` | Fakultät für Wirtschaftswissenschaften — Akzent im **Dunkelmodus** |
| Wortmarken-Schwarz | `#161616` | Textfarbe der htw-saar-Wortmarke |
| AuB-Grün (abgedunkelt) | `#5C6B14` | Fakultätsfarbe, als Erfolgsfarbe verwendet |

Dazu kommt der **Vierfarbbalken** aus `assets/favicon.png` — Grün, Blau,
Magenta, Orange. Er ist die Klammer über alle vier Fakultäten und steht an genau
einer Stelle: unter der Wortmarke in der Navigationsleiste.

Die beiden Modi tragen unterschiedliche Logos, weil beide Varianten mitgeliefert
sind und jede auf ihrem Untergrund funktioniert:

* **Hell** — die reine schwarze Wortmarke (`htwsaar_Logo_LA.png`) plus
  Vierfarbbalken. Die Kompaktvariante mit dem Zusatztext daneben wäre in einer
  232 px breiten Leiste unleserlich.
* **Dunkel** — das goldene Fakultätslogo (`htwsaar_Logo_wiwi.png`); es leuchtet
  auf dunklem Grund von selbst und macht den Balken überflüssig.

Vier Regeln bestimmen das ganze Bild:

1. **Der Akzent markiert nur die eine Aktion pro Bildschirm, die Geld oder
   Lagerbestand verändert** — und den aktiven Navigationseintrag. Welche Farbe
   das ist, hängt am Modus: htw-Blau im Hellmodus, WiWi-Gold im Dunkelmodus.
   Der Akzent folgt damit dem Logo, das im selben Modus in der Leiste steht.
2. **Zahlen sind dickengleich und rechtsbündig.** In einer Kasse liest niemand
   Zeilen, man vergleicht Spalten.
3. **Der Radius sagt, was ein Element ist:** 0 px randlose Fläche, 6 px
   Bedienelement, 8 px Karte, 12 px Dialog.
4. **Karten liegen heller auf der Seite.** Tiefe entsteht durch Tonwert, nicht
   durch Schatten — im Dunkelmodus seitenverkehrt.

Die Werte liegen dreifach vor und müssen zusammen gepflegt werden:

```
DESIGN.md                          ← Quelle der Wahrheit (mit Begründung)
  ├── fanshop/gui/htw_saar_theme.json   ← Format für CustomTkinter
  └── fanshop/gui/design.py             ← Konstanten für den GUI-Code
```

---

## 9. Warum SQLite und CustomTkinter

**SQLite** — verlangt vom Pflichtenheft und für den Zweck genau richtig: kein
Serverprozess, die ganze Datenbank ist eine Datei, die man kopieren oder per
USB-Stick weitergeben kann. Die ACID-Eigenschaften erfüllen /NF30/ ohne eigenes
Zutun. `sqlite3` ist Teil der Python-Standardbibliothek.

**CustomTkinter** — ebenfalls vom Pflichtenheft vorgegeben. Es baut auf dem
mitgelieferten `tkinter` auf, sieht aber zeitgemäß aus und bringt den
Dunkelmodus mit (/F54/). Der Preis: Es fehlt ein Tabellen-Widget, deshalb
steckt in `bausteine.Tabelle` ein `ttk.Treeview`, dessen Farben von Hand
gesetzt werden müssen.

---

## 10. Wenn etwas erweitert werden soll

| Vorhaben | Anzufassen |
|---|---|
| Neues Feld an einem Artikel | `schema.sql`, `modelle/artikel.py`, `repositories/artikel_repository.py`, `gui/seite_artikel.py` |
| Neue Rabattart | `modelle/sonderaktion.py` und `Warenkorb.berechne()` |
| Neue Auswertung | `repositories/bericht_repository.py`, `logik/bericht_service.py`, `gui/seite_berichte.py` |
| Neue Seite | Klasse von `BasisSeite` ableiten und in `gui/app.py` eintragen |
| Neue Zugangsart | `zugriff.py` ergänzen und den Seitenaufbau in `gui/app.py` prüfen |
| Neuer Schritt in der Kasse | `SCHRITT_*`-Konstante, `_schritt_X_bauen()` und ein Eintrag in `self.schritte` in `gui/seite_kasse.py` |
| Andere Größenspanne | `GROESSEN_JE_KATEGORIE` in `konfiguration.py` — Damen und Herren getrennt |
| Neues Stickermotiv | Bild nach `assets/sticker/`, Eintrag in `MOTIVE` in `modelle/sticker.py`. Achtung: `STICKER_PRO_EINKAUF` × `STARTERSET_MINDESTBESTELLUNGEN` sollte weiterhin der Zahl der Motive entsprechen |
| Anderer Setinhalt oder andere Bedingung | `STARTERSET_INHALT` bzw. `STARTERSET_MINDESTBESTELLUNGEN` in `konfiguration.py` |
| Farbe ändern | zuerst `DESIGN.md`, dann `design.py` und `htw_saar_theme.json` — beide Modi im selben Farbpaar |

Die Reihenfolge ist immer dieselbe: von unten nach oben durch die Schichten.
