# WI Fanshop — Kassensystem und Warenwirtschaft

Desktop-Kassensystem für den Verkaufsstand „WI Fanshop" der htw saar.
Softwareprojekt **WINF-B25-450**, Sommersemester 2026, **Gruppe 10**.

Die Anwendung bildet den Verkauf am Point of Sale ab: Artikel suchen, Warenkorb
zusammenstellen, Rabatte berechnen, kassieren, Sticker ausgeben, Retouren
annehmen und der Shop-Leitung Berichte liefern. Sie läuft vollständig lokal,
ohne Internet und ohne Server.

![Kasse, Schritt 2](docs/bilder/kasse-artikel-hell.png)

---

## Technische Eckdaten

| | |
|---|---|
| **Sprache** | Python 3.14 (objektorientiert) |
| **Oberfläche** | CustomTkinter 5.2+ |
| **Datenbank** | SQLite (eine lokale Datei `fanshop.db`) |
| **Diagramme** | matplotlib (optional, nur für die Kann-Kriterien) |
| **Tests** | `unittest` aus der Standardbibliothek — 94 Tests |
| **Betriebssysteme** | Windows, macOS, Linux |
| **Fenstergröße** | mindestens 1280 × 800 |
| **Umfang** | rund 8.000 Zeilen Python in 50 Dateien |
| **Externe Dienste** | keine — die Anwendung ist Offline-First |

---

## Quickstart

**Voraussetzung:** Python 3.11 oder neuer (entwickelt mit 3.14).
Prüfen mit `python --version`.

```bash
git clone <repository-url>
cd SoftwareprojektSoSe26
pip install -r requirements.txt
python main.py
```

Das war alles. Beim ersten Start passiert automatisch:

1. Die Datenbank `fanshop.db` wird im Projektverzeichnis angelegt.
2. Alle Tabellen werden erzeugt.
3. Testdaten werden eingespielt: 31 Artikel mit echten Produktfotos und den
   Preisen des htw-saar-Webshops, 5 Kunden, 2 Sonderaktionen und 8
   Beispielbestellungen der letzten Wochen — samt gefüllten Sticker-Alben.

Bei jedem weiteren Start wird nichts überschrieben — die Anwendung startet mit
den vorhandenen Daten.

### Zugang wählen

Vor dem Öffnen der Anwendung wird die Zugangsart ausgewählt:

- **Kunde**: kann ausschließlich die Seite **Kasse** nutzen.
- **Kassierer**: hat Zugriff auf alle Bereiche der Anwendung.

### Von vorne anfangen

Datenbankdatei löschen und neu starten:

```bash
python main.py
```

(vorher `fanshop.db` löschen — die Datei liegt im Projektverzeichnis)

### Tests ausführen

```bash
python -m unittest discover -s tests -t . -v
```

---

## Die fünf Fachseiten

| Seite | Wofür | Anforderungen |
|---|---|---|
| **Kasse** | Geführte Strecke in vier Schritten bis zum gebuchten Kauf | /F11/–/F14/, /F52/, /F53/ |
| **Sortiment** | Artikel anlegen, pflegen, deaktivieren, durchsuchen, Produktfoto zuweisen, Sonderaktionen schalten | /F21/–/F23/ |
| **Kunden** | Kartei, Suche, Newsletter-Anmeldung, Sticker-Konto | /F41/–/F44/, /F52/ |
| **Retouren** | Bestellung suchen, Ware zurücknehmen, Erstattung | /F51/ |
| **Berichte** | Kennzahlen je Zeitraum, Ranglisten, Diagramme | /F31/–/F313/, /F24/–/F27/ |

Nach der Zugangsart richtet sich, welche dieser Seiten aufgebaut werden:
**Kunde** sieht nur die Kasse, **Kassierer** die vollständige Navigation.
Ganz unten in der Navigation liegt auch der Schalter zwischen Hell- und
Dunkelmodus (/F54/).

---

## Ein typischer Verkauf

Die Kasse führt durch vier Schritte — oben sieht man immer, wo man steht, unten
geht es mit **Zurück** und **Weiter**:

**1. Kunde** — in der Liste suchen und anklicken, oder „Ohne Kundenkonto verkaufen".
Rechts stehen Anschrift, Stickerstand und ein offener Newsletter-Gutschein.

**2. Artikel** — über Suchfeld, Kategorie oder Preisspanne finden. Die markierte
Zeile zeigt rechts das Produktfoto mit Preis und Bestand. Menge eintragen,
**In den Warenkorb** — oder Doppelklick auf die Zeile.

Oben in der Strecke sieht man jederzeit, wo man steht; anklicken springt zurück
und, wenn schon Ware im Korb liegt, auch vorwärts.

**3. Warenkorb** — Mengen ändern, Positionen entfernen. Rechts steht jede
Rabattzeile einzeln: Artikelrabatt, laufende Sonderaktion, Newsletter-Gutschein.

**4. Abschluss** — der fertige Beleg mit Endbetrag. **Kauf abschließen** bucht
Bestellung und Rechnung, zieht den Lagerbestand ab und zeigt die drei
Sammelsticker, die der Kunde bekommt.

![Kasse, Schritt 4](docs/bilder/kasse-abschluss-hell.png)

---

## Projektstruktur

```
SoftwareprojektSoSe26/
├── main.py                  Startpunkt
├── DESIGN.md                Designsystem (Farben, Schriften, Regeln)
├── requirements.txt
├── fanshop/
│   ├── konfiguration.py     Pfade, Kategorien, Rabattsätze
│   ├── fehler.py            eigene Fehlerklassen
│   ├── hilfsmittel.py       Formatierung, Datum, Zahlen
│   ├── zugriff.py           erlaubte Seiten je Zugangsart
│   ├── datenbank/           SQLite-Verbindung, Schema, Testdaten
│   ├── modelle/             Fachklassen (Artikel, Kunde, Warenkorb …)
│   ├── repositories/        Datenzugriff — der einzige Ort mit SQL
│   ├── logik/               Geschäftslogik (Kasse, Retouren, Berichte)
│   └── gui/                 Oberfläche (CustomTkinter)
├── tests/                   94 automatische Tests
├── specs/                   ein Kurzsteckbrief je Baustein
├── docs/                    Dokumentation (siehe unten)
└── assets/                  Produktfotos, Sticker, htw-saar-Logos
```

---

## Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/Architektur.md](docs/Architektur.md) | Schichten, Entwurfsentscheidungen, Datenmodell, Abweichungen vom Pflichtenheft |
| [docs/Technische-Dokumentation.md](docs/Technische-Dokumentation.md) | Was steckt wo — Datei für Datei, jede Anforderung mit Fundstelle |
| [DESIGN.md](DESIGN.md) | Designsystem: Farben der htw saar, Schriften, Gestaltungsregeln |
| [docs/Commit-Plan.md](docs/Commit-Plan.md) | In welcher Reihenfolge das Projekt ins Repository kommt |
| [specs/09-sticker.md](specs/09-sticker.md) | Das Sammelalbum: sechs Motive, drei pro Kauf |
| [specs/](specs/) | Kurzsteckbriefe der einzelnen Bausteine |

---

## Aufbau in vier Schichten

```
GUI  →  Logik (Services)  →  Repositories  →  Datenbank
```

Jede Schicht kennt nur die Schicht unter sich. Die Oberfläche enthält keine
Rechnung und kein SQL; die Geschäftslogik läuft vollständig ohne Fenster —
genau das machen die 94 Tests. Details in
[docs/Architektur.md](docs/Architektur.md).

---

## Bekannte Grenzen

Bewusst nicht umgesetzt (so im Pflichtenheft, Kapitel 1.3, festgelegt):

- kein Online-Shop, keine Weboberfläche, keine Netzwerkfunktion
- kein Zahlungsdienstleister — die Rechnung gilt ab Kauf als bezahlt
- kein Versand, nur Mitnahmemodus
- kein Mehrbenutzerbetrieb, keine Benutzeranmeldung
- ein aktiver Kunde pro Vorgang
- keine Anmeldung: Die Zugangsart begrenzt die sichtbaren Bereiche, ist aber
  kein passwortgeschütztes Berechtigungssystem

---

## Team

Gruppe 10: Lukas Ley, Tim Daniel, Sebastian Uli Froschauer, Emir Impis Sali,
Michail Iliev.

Betreuung: Prof. Dr. Daniel F. Abawi, Michael B. Schmidt —
Fakultät für Wirtschaftswissenschaften, htw saar.
