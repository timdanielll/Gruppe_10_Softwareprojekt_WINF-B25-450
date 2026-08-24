# Spec 00 — Projektaufbau und Schichtenmodell

**Status:** fertig
**Meilenstein:** Vorbereitung

## Ziel

Grundgerüst des Projekts festlegen, bevor irgendein Feature entsteht: Ordner,
Abhängigkeiten, Schichten und deren Aufrufrichtung.

## Dateien

| Datei | Zweck |
|---|---|
| `main.py` | Startpunkt des Programms |
| `requirements.txt` | Abhängigkeiten (customtkinter, Pillow, matplotlib) |
| `.gitignore` | schließt `fanshop.db`, `__pycache__` u. a. aus |
| `fanshop/__init__.py` | Paketbeschreibung, erklärt die Schichten |
| `fanshop/konfiguration.py` | Pfade, Kategorien, Rabattsätze, Stickeranzahl |
| `fanshop/fehler.py` | eigene Fehlerklassen |
| `fanshop/hilfsmittel.py` | Formatierung (Euro, Prozent), Datums- und Zahlenumwandlung |
| `fanshop/zugriff.py` | erlaubte Seiten je Zugangsart (`kunde`, `kassierer`) |

## Schichten (/NF21/)

```
GUI  ->  Logik (Services)  ->  Repositories  ->  Datenbank
```

Jede Schicht kennt **nur** die Schicht unter sich. Rückwärts gibt es keine
Importe. Konkret heißt das:

- Die GUI importiert nie ein Repository und nie `sqlite3`.
- Die Logik importiert nie `customtkinter`.
- Die Modelle importieren weder das eine noch das andere.

Prüfen lässt sich das mit einem Blick in die Importzeilen — deshalb stehen alle
Importe oben in der Datei und keiner mitten im Code (Ausnahme: zwei bewusst
lokale Importe in `hilfsmittel.py`, um einen Ringimport zu vermeiden).

## Entscheidungen

1. **Deutsche Bezeichner im Fachcode.** Klassen und Methoden heißen `Artikel`,
   `warenkorb.hinzufuegen()`, `kunden_repository.suchen()`. Damit stehen die
   Begriffe aus dem Pflichtenheft direkt im Quelltext und niemand muss beim
   Lesen übersetzen. Technische Begriffe (`Repository`, `Service`) bleiben
   englisch, weil sie als Muster bekannt sind.
2. **Umlaute nur in Texten, die der Benutzer sieht.** Kommentare und Docstrings
   sind bewusst umlautfrei geschrieben (`Groesse`, `koennen`), damit sie in
   jedem Editor und jeder Konsole gleich aussehen. GUI-Texte, Fehlermeldungen
   und Testdaten benutzen selbstverständlich echte Umlaute.
3. **Anforderungs-IDs im Code.** Jede Methode, die eine Anforderung erfüllt,
   nennt ihre ID im Docstring (`/F13/`, `/NF30/`). So lässt sich das
   Pflichtenheft gegen den Code prüfen, ohne zu suchen.
4. **Zugang unabhängig von Widgets.** Die Zuordnung von Zugangsart zu Seiten
   liegt in `fanshop/zugriff.py`, nicht in der GUI. Dadurch lässt sie sich ohne
   geöffnetes Fenster testen und die Oberfläche baut für Kunden gesperrte
   Seiten gar nicht erst auf.

## Nächster Schritt

Spec 01 — Datenbankschicht.
