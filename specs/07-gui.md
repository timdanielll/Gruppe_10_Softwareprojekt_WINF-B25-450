# Spec 07 — Benutzeroberfläche

**Status:** fertig
**Meilenstein:** 3 (GUI-Frontend, Soll 31.08.2026)
**Anforderungen:** /NF10/, /NF11/, /NF12/, /NF21/, /F54/ und alle Masken aus Kapitel 7

## Ziel

Alle Funktionen über eine grafische Oberfläche bedienbar machen — ohne dass
Rechenlogik oder SQL in die GUI wandert.

## Dateien

| Datei | Inhalt |
|---|---|
| `gui/design.py` | Farben, Schriften, Abstände (aus `DESIGN.md`) |
| `gui/htw_saar_theme.json` | dieselben Werte für CustomTkinter |
| `gui/bausteine.py` | `Panel`, `Feld`, `Tabelle` (mit Zeilenmarkierung), `Dialog`, `Schrittleiste`, `Statuszeile`, `Bildkarte`, `Kachel`, `StickerAlbum`, `HtwBalken`, Knöpfe |
| `gui/basis_seite.py` | `BasisSeite` — Basisklasse aller Seiten |
| `fanshop/zugriff.py` | Seitenzuordnung für Kunde und Kassierer — ohne GUI-Abhängigkeit |
| `gui/app.py` | Rollenauswahl, Hauptfenster und rollenabhängige Navigation |
| `gui/seite_kasse.py` | /F11/–/F14/, /F52/, /F53/ — als Wizard mit vier Schritten |
| `gui/seite_artikel.py` | /F21/–/F23/ plus Schalten der Sonderaktionen und der Hinweis auf das dauerhafte Starterset-Sonderangebot (/F53/) |
| `gui/seite_kunden.py` | /F41/–/F44/, /F52/ |
| `gui/seite_retouren.py` | /F51/ |
| `gui/seite_berichte.py` | /F31/–/F313/, /F24/–/F27/ |

## Aufbau

```
+----------------+--------------------------------------------+
| Navigation     |  Arbeitsbereich                            |
| 232 px         |  Karten auf abgetönter Seite               |
+----------------+--------------------------------------------+
```

## Zugangsart vor dem Hauptfenster

Beim Programmstart erscheint zuerst eine kompakte Auswahl mit den zwei
Schaltflächen **„Als Kunde fortfahren“** und **„Als Kassierer fortfahren“**.
Erst nach dieser Wahl baut `FanshopApp` die Navigation und die Fachseiten auf:

| Zugangsart | Navigation und angelegte Seiten |
|---|---|
| **Kunde** | ausschließlich **Kasse** |
| **Kassierer** | **Kasse**, **Sortiment**, **Kunden**, **Retouren**, **Berichte** |

Die Zuordnung liegt in `fanshop/zugriff.py`. `app._rolle_waehlen()` übernimmt
sie und erzeugt nur die erlaubten Seiten; eine Kundensitzung enthält die
Verwaltungsseiten deshalb nicht einmal im Speicher. Die Zugangsart wird bei
jedem Start neu gewählt. Sie ist bewusst **keine Anmeldung** und enthält weder
Passwort noch Benutzerverwaltung.

### Die Kasse ist eine Strecke, keine Maske

Ursprünglich standen alle vier Bereiche der Kasse gleichzeitig auf einem
Bildschirm — das war voll und unübersichtlich. Jetzt führt die Seite durch vier
Schritte (`SCHRITT_KUNDE`, `SCHRITT_ARTIKEL`, `SCHRITT_KORB`,
`SCHRITT_ABSCHLUSS`), oben die `Schrittleiste`, unten „Zurück" und „Weiter".

Das ist zugleich die wörtlichste Umsetzung von /NF12/: „Der Kassiervorgang muss
einem logischen, linearen Ablauf folgen."

Alle vier Schritte werden beim Aufbau **einmal** angelegt und danach nur ein-
und ausgeblendet — genau wie die für die gewählte Zugangsart erlaubten Seiten
im Hauptfenster. Der Warenkorb lebt im `KassenService`, nicht in einem Schritt;
deshalb geht beim Blättern nichts verloren.

Die Schrittleiste ist in **beide** Richtungen anklickbar. Sie kennt die
fachlichen Regeln aber nicht, sondern reicht den gewünschten Schritt an die
Seite durch (`_schritt_angefordert`). Vorwärts wird dort Schritt für Schritt
über dieselbe Prüfung geführt wie der Knopf „Weiter" — man kann also vom
Artikelschritt direkt auf „Abschluss" klicken, wenn Ware im Korb liegt, aber
den Warenkorb nicht mit leerem Korb überspringen.

### Rückmeldung statt Bestätigungsdialog

`BasisSeite` bringt eine `Statuszeile` mit und die Methode `melden()`. Nach
jeder geglückten Aktion steht dort ein Satz („2 × Lineal htw saar in den
Warenkorb."), der nach vier Sekunden verblasst. Dialoge bleiben Fehlern,
Sicherheitsabfragen und dem Kaufabschluss vorbehalten — ein Dialog, den man
wegklicken muss, ist für eine Kasse die falsche Rückmeldung.

Die erlaubten Seiten werden **einmal** angelegt und danach nur ein- und
ausgeblendet. Im Kassiererzugang sind das alle fünf Fachseiten, im
Kundenzugang nur die Kasse. Dadurch bleiben Suchtext, Filter und Auswahl
erhalten, wenn man kurz auf eine andere Seite wechselt. Beim Einblenden ruft
`app.seite_zeigen()` die Methode `beim_anzeigen()` der Seite auf, die dort
frische Daten lädt.

## Die drei Methoden jeder Seite

Jede Seite erbt von `BasisSeite` und überschreibt bis zu drei Methoden:

| Methode | Wann | Wofür |
|---|---|---|
| `aufbauen()` | einmal | Widgets anlegen |
| `beim_anzeigen()` | bei jedem Seitenwechsel | Daten neu laden |
| `stil_aktualisieren()` | nach Hell/Dunkel-Wechsel | Tabellen umfärben |

## Warum `Tabelle` ein eigener Baustein ist

CustomTkinter bringt kein Tabellen-Widget mit. `bausteine.Tabelle` kapselt
deshalb einen `ttk.Treeview` und ergänzt drei Dinge, die man sonst fünfmal
nachbauen müsste:

1. **Farben passend zum Modus.** `ttk` kennt Hell/Dunkel von CustomTkinter
   nicht — `stil_anwenden()` setzt die Farben von Hand und wird nach jedem
   Umschalten erneut aufgerufen.
2. **Schlüssel statt Zeilenindex.** `fuellen()` bekommt Paare aus ID und
   Werten, `gewaehlter_schluessel()` gibt die ID der markierten Zeile zurück.
   So muss keine Seite Zeilennummern auf Datensätze umrechnen.
3. **Leerzustand.** Ist die Liste leer, erscheint ein Satz, der sagt, was zu
   tun ist („Keine Artikel gefunden. Filter zurücksetzen?") — keine leere
   graue Fläche.
4. **Zeilenmarkierung.** `fuellen(..., markierungen={id: "erledigt"})` färbt
   einzelne Zeilen grau. Damit lässt sich ein Zustand zeigen, statt ihn per
   Fehlermeldung zu erklären.
5. **Selbstrechnende Spaltenbreiten.** `_breiten_anpassen()` hängt an
   `<Configure>` und verteilt bei jeder Größenänderung den vorhandenen Platz:
   erst das gemessene Minimum je Überschrift, dann der Überschuss an die
   breiteste Spalte, bei Platzmangel anteilig kürzen. Ohne das schneidet `ttk`
   die letzte Spalte einfach ab — eine waagerechte Bildlaufleiste gibt es
   nicht. Die Breiten im Quelltext sind nur ein Vorschlag.

## Fehlerbehandlung (/NF11/)

Jede Aktion einer Seite folgt demselben Muster:

```python
try:
    ergebnis = self.anwendung.irgendein_service.mach_was(...)
except FanshopFehler as fehler:
    self.fehler_anzeigen(fehler)   # Dialogfenster mit dem Text aus der Logik
    return
```

Der Meldungstext steht nur an einer Stelle im Projekt: dort, wo das Problem
festgestellt wird. Bei Eingabefeldern erscheint der Text zusätzlich als rote
Zeile unter dem Feld — ein Dialog verschwindet, der Fehler bleibt.

## Bedienungsentscheidungen

- **Suche mit Verzögerung.** Die Volltextsuche startet 250 ms nach dem letzten
  Tastendruck (`after_cancel` / `after`), nicht bei jedem Buchstaben.
- **Sichtbare Beschriftungen.** Jedes Feld hat eine Beschriftung darüber;
  Platzhaltertext ist nur ein Beispiel, nie die Beschriftung.
- **Ein goldener Knopf pro Bildschirm.** Er trägt die unwiderrufliche Aktion.
- **Sicherheitsabfrage** vor Löschen, Deaktivieren und Korb-Leeren.
- **Doppelklick** auf einen Artikel in der Kasse legt ihn in den Warenkorb.
- **Felder springen nicht.** Stehen mehrere Felder nebeneinander und eines
  bekommt eine Fehlerzeile, wird es höher — `pack` würde die Nachbarn neu
  zentrieren und sie rutschten nach unten. Deshalb werden nebeneinander
  liegende Felder mit `anchor="n"` gesetzt.
- **Zustand zeigen statt erklären.** Eine vollständig zurückgegebene
  Retourenposition wird grau markiert und zeigt „zurück" statt einer 0. Erst
  wenn jemand sie trotzdem anklickt, kommt eine Zeile in der Statuszeile —
  kein Dialog.
- **Produktfoto zuweisen.** Ein neuer Artikel hat kein Foto. Die Auswahlliste
  „Produktfoto" bietet die vorhandenen Bilder aus `assets/artikel/` an,
  beschriftet mit dem Titel des Artikels, der sie schon benutzt.
- **Knöpfe bleiben erreichbar.** Artikelmaske und Kundenmaske sind länger als
  die Karte hoch ist. In beiden liegen die Felder in einer
  `CTkScrollableFrame`, während die Schaltflächen mit `side="bottom"` fest am
  unteren Rand verankert sind — pack reserviert ihren Platz, bevor der Rest
  gefüllt wird.
- **Sonne und Mond** statt der Beschriftung „Hell/Dunkel" — das Symbolpaar
  (`☀` U+2600 und `☽` U+263D) braucht keine Überschrift und ist in jeder
  Sprache dasselbe.
- **Zugang vor Inhalt.** Die Rollenwahl wird vor Navigation und Seiten
  gezeigt. Beide Auswahlknöpfe sind sekundär: Sie wählen eine Ansicht, lösen
  aber keine fachliche oder unwiderrufliche Aktion aus.

## Grenzen

- Die Diagramme öffnen ein eigenes Fenster. matplotlib wird erst beim Klick
  importiert; fehlt es, erscheint ein Hinweis und die Anwendung läuft weiter.
- Feste Mindestgröße 1280 × 800. Ein Kassenrechner hat einen bekannten
  Bildschirm; ein responsives Umbruchverhalten wäre erfundene Komplexität.
- Die Rollenwahl ist kein Sicherheitssystem. Wer Verwaltungszugriff
  verlässlich schützen muss, braucht zusätzlich eine Anmeldung.
- Tkinter kennt keine Laufweite (`letterSpacing`). Die Werte aus `DESIGN.md`
  gelten für Belege und Berichte, in der Oberfläche werden Versallabels durch
  zusätzlichen Innenabstand geöffnet.

## Nächster Schritt

Spec 08 — Tests.
