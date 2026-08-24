# Spec 06 — Designsystem „Kassenpult"

**Status:** fertig
**Anforderungen:** /NF10/ (ansprechende GUI), /F54/ (Dark-Mode)

## Ziel

Ein verbindliches, begründetes Aussehen für die ganze Anwendung — abgeleitet
aus dem Corporate Design der htw saar, damit die Software aussieht, als gehöre
sie zur Hochschule.

## Dateien

| Datei | Zweck |
|---|---|
| `DESIGN.md` | Quelle der Wahrheit: alle Farben, Schriften, Abstände + Begründung |
| `fanshop/gui/htw_saar_theme.json` | dieselben Werte als CustomTkinter-Theme |
| `fanshop/gui/design.py` | dieselben Werte als Python-Konstanten für den GUI-Code |

Reihenfolge beim Ändern: **erst `DESIGN.md`, dann die beiden anderen Dateien
nachziehen.**

## Herkunft der Farben

Nicht erfunden, sondern aus dem Corporate Design der htw saar entnommen
(nachgeprüft im Stylesheet von htwsaar.de und in den Logos unter `assets/`):

| Farbe | Wert | Herkunft |
|---|---|---|
| htw-Blau, aufgehellt | `#4CC2EE` | Vierfarbbalken-Blau (`#00A8E7`) um 30 % aufgehellt — Akzent im Hellmodus |
| WiWi-Gold | `#F7A823` | Fakultät für Wirtschaftswissenschaften (CSS-Klasse `.layout-wiwi`) — Akzent im Dunkelmodus |
| Wortmarken-Schwarz | `#161616` | Textfarbe der htw-saar-Wortmarke |
| AuB-Grün | `#AFCB34` | Fakultätsfarbe, abgedunkelt zu `#5C6B14` als Erfolgsfarbe |

Zum Vergleich die weiteren Fakultätsfarben, die **nicht** verwendet werden:
IngWi `#20A6DF`, SoWi `#E7348B`.

## Die drei Regeln, die man kennen muss

1. **Der Akzent nur für die eine Aktion pro Bildschirm, die Geld oder
   Lagerbestand verändert** — und für den aktiven Navigationseintrag. Sonst
   nirgends. Er ist **nie** Schriftfarbe; dafür gibt es `rabatt` (`#8A5A05`).

   **Je Modus ein eigener Akzent:** htw-Blau `#4CC2EE` im Hellmodus,
   WiWi-Gold `#F7A823` im Dunkelmodus. Das ist dieselbe Trennung wie beim
   Logo — hell die allgemeine Wortmarke, dunkel das Fakultätslogo. Im Code
   steht dafür genau ein Name: `farbe("akzent")` liefert das Paar, und
   CustomTkinter schaltet um.
2. **Zahlen sind dickengleich und rechtsbündig.** Jeder Betrag, jede Menge und
   jede laufende Nummer wird in einer `zahl`-Schriftrolle gesetzt (Consolas /
   Menlo / DejaVu Sans Mono). In einer Kasse liest niemand Zeilen, man
   vergleicht Spalten.
3. **Der Radius sagt, was ein Element ist.** 0 px für randlose Flächen
   (Navigationsleiste, Tabellen), 6 px für Bedienelemente (Buttons, Felder),
   8 px für Karten, 12 px ausschließlich für den modalen Dialog.
4. **Karten liegen heller auf der Seite.** Tiefe entsteht durch Tonwert — im
   Dunkelmodus seitenverkehrt.

5. **Erfolg meldet sich in der Statuszeile, nicht im Dialog.** Ein Dialog, den
   man wegklicken muss, um weiterzuarbeiten, ist für eine Kasse die falsche
   Rückmeldung. Dialoge bleiben Fehlern, Sicherheitsabfragen und dem
   Kaufabschluss vorbehalten.

Dazu: keine Schatten, keine Farbverläufe, keine eingefärbten Kategorien.
Trennung passiert durch Abstand, notfalls durch eine 1-px-Haarlinie.

## Der Vierfarbbalken

Aus `assets/favicon.png` stammen die vier Farben, mit denen die htw saar alle
Fakultäten zusammenfasst: Grün `#AFCB05`, Blau `#00A8E7`, Magenta `#E82C8A`,
Orange `#F7A600`. Sie erscheinen an **genau einer** Stelle — als 4 px hoher
Streifen unter der Wortmarke in der Navigationsleiste.

Die beiden Modi tragen unterschiedliche Logos: Im Hellmodus die reine schwarze
Wortmarke (`htwsaar_Logo_LA.png`) mit dem Balken darunter — nicht die
Kompaktvariante, deren Zusatzzeile in der schmalen Leiste unleserlich wäre —, im
Dunkelmodus das goldene Fakultätslogo (`htwsaar_Logo_wiwi.png`), das den Balken
überflüssig macht. Welches geladen wird, entscheidet `design.logo_datei()`.

## Schriften

Die Hausschrift **Akkurat** ist kommerziell lizenziert und darf nicht
mitgeliefert werden. Statt dessen wählt `design.schriftfamilie()` zur Laufzeit
die erste vorhandene Schrift:

- Text: Segoe UI (Windows) → Helvetica Neue (macOS) → DejaVu Sans (Linux)
- Zahlen: Consolas → Menlo → DejaVu Sans Mono

Nur zwei Schnitte (400 und 700). Grund ist auch technisch: Tkinter löst
Zwischenschnitte auf keinem Betriebssystem verlässlich auf.

## Dark-Mode (/F54/)

Keine Invertierung, sondern dieselbe Palette auf der anderen Seite: warmes
Anthrazit (`#1A1815`) statt blaustichigem Marineblau, gebrochenes Warmweiß
(`#EDE9E1`) statt reinem Weiß, Gold unverändert. Umgeschaltet wird mit
`design.modus_umschalten()` über den Schalter unten in der Navigationsleiste.

## Zugangsart

Die Anwendung beginnt mit einer kompakten Auswahlkarte für **Kunde** und
**Kassierer**. Beide Schaltflächen sind sekundär: Sie wählen nur den Umfang der
nachfolgenden Ansicht und verändern keine Daten. Im Kundenzugang wird allein
die Kasse aufgebaut, im Kassiererzugang alle fünf Fachseiten. Erst danach gilt
das reguläre Layout mit linker Navigationsleiste.

Die Zugangsart ist keine Authentifizierung. Sie ersetzt weder Passwort noch
Benutzerverwaltung und wird bei jedem Programmstart neu ausgewählt.

## Prüfung

`DESIGN.md` folgt dem DESIGN.md-Format von Google und wurde mit dem offiziellen
Linter geprüft:

```bash
npx -y -p @google/design.md designmd lint --format json DESIGN.md
```

Ergebnis: **0 Fehler, 0 Warnungen.** Alle Farbpaare erfüllen WCAG AA (Kontrast
mindestens 4,5:1) — geprüft in beiden Modi.

## Nächster Schritt

Spec 07 — GUI-Grundgerüst.
