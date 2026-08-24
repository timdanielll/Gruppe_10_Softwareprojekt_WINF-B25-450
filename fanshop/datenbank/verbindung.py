"""Verbindung zur SQLite-Datenbank.

Diese Klasse ist die einzige Stelle im Programm, die das Modul ``sqlite3``
direkt benutzt. Alle Repositories bekommen ein ``Datenbank``-Objekt uebergeben
und rufen darauf nur noch die vier Methoden
``abfragen``, ``abfragen_eine``, ``ausfuehren`` und ``ausfuehren_viele`` auf.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fanshop import konfiguration


class Datenbank:
    """Kapselt die SQLite-Datei und stellt einfache Hilfsmethoden bereit."""

    def __init__(self, pfad: Path | str | None = None) -> None:
        """Legt die Verbindung an.

        :param pfad: Pfad zur Datenbankdatei. ``None`` benutzt den Standardpfad
                     aus der Konfiguration, ``":memory:"`` erzeugt eine reine
                     Testdatenbank im Arbeitsspeicher.
        """
        self.pfad = str(pfad) if pfad is not None else str(konfiguration.DATENBANK_DATEI)
        self.verbindung = sqlite3.connect(self.pfad)

        # Zeilen sollen sich wie ein Dictionary ansprechen lassen:
        # zeile["titel"] statt zeile[2]. Das macht den Code lesbarer.
        self.verbindung.row_factory = sqlite3.Row

        # SQLite prueft Fremdschluessel nur, wenn man es ausdruecklich einschaltet.
        self.verbindung.execute("PRAGMA foreign_keys = ON")

    # -- Schema ------------------------------------------------------------

    def schema_anlegen(self) -> None:
        """Fuehrt schema.sql aus und legt damit alle Tabellen an (/NF30/)."""
        sql = konfiguration.SCHEMA_DATEI.read_text(encoding="utf-8")
        self.verbindung.executescript(sql)
        self.verbindung.commit()
        self._schema_nachziehen()

    def _schema_nachziehen(self) -> None:
        """Bringt eine aeltere ``fanshop.db`` auf den aktuellen Stand.

        ``CREATE TABLE IF NOT EXISTS`` legt bestehende Tabellen nicht neu an -
        neue Spalten fehlen dort also. Wer die Anwendung schon benutzt hat, soll
        seine Datenbank aber nicht loeschen muessen. Deshalb werden hier genau
        die Spalten nachgetragen, die seit der ersten Fassung dazugekommen
        sind, und der Sammelstand auf die neue Regel "jedes Motiv nur einmal"
        umgestellt.
        """
        nachtrag = [
            ("kunde", "starterset_erhalten", "INTEGER NOT NULL DEFAULT 0"),
            ("bestellung", "starterset_ausgegeben", "INTEGER NOT NULL DEFAULT 0"),
        ]

        with self.verbindung:
            for tabelle, spalte, typ in nachtrag:
                vorhandene = {
                    zeile["name"]
                    for zeile in self.verbindung.execute(f"PRAGMA table_info({tabelle})")
                }
                if spalte not in vorhandene:
                    self.verbindung.execute(
                        f"ALTER TABLE {tabelle} ADD COLUMN {spalte} {typ}"
                    )

            # Frueher konnte dasselbe Motiv mehrfach gutgeschrieben werden.
            # Jetzt ist jeder Sticker einmalig: doppelte Gutschriften werden auf
            # eine reduziert und der Zaehler an das Album angeglichen, damit
            # beide Staende wieder zusammenpassen.
            self.verbindung.execute("UPDATE kunde_sticker SET anzahl = 1 WHERE anzahl <> 1")
            self.verbindung.execute(
                """UPDATE kunde
                   SET sticker_kontostand = (
                           SELECT COUNT(*) FROM kunde_sticker s
                           WHERE s.kundennummer = kunde.kundennummer
                       )
                   WHERE sticker_kontostand <> (
                           SELECT COUNT(*) FROM kunde_sticker s
                           WHERE s.kundennummer = kunde.kundennummer
                       )"""
            )

    # -- Lesen -------------------------------------------------------------

    def abfragen(self, sql: str, parameter: tuple = ()) -> list[sqlite3.Row]:
        """Fuehrt ein SELECT aus und gibt alle Zeilen als Liste zurueck."""
        cursor = self.verbindung.execute(sql, parameter)
        return cursor.fetchall()

    def abfragen_eine(self, sql: str, parameter: tuple = ()) -> sqlite3.Row | None:
        """Fuehrt ein SELECT aus und gibt die erste Zeile zurueck (oder None)."""
        cursor = self.verbindung.execute(sql, parameter)
        return cursor.fetchone()

    # -- Schreiben ---------------------------------------------------------

    def ausfuehren(self, sql: str, parameter: tuple = ()) -> int:
        """Fuehrt INSERT/UPDATE/DELETE aus und speichert die Aenderung sofort.

        :return: Bei INSERT die neu vergebene ID, sonst die Anzahl der
                 geaenderten Zeilen.
        """
        with self.verbindung:  # commit bei Erfolg, rollback bei Fehler
            cursor = self.verbindung.execute(sql, parameter)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    def ausfuehren_viele(self, sql: str, parameterliste: list[tuple]) -> None:
        """Fuehrt dieselbe Anweisung fuer viele Parametersaetze aus."""
        with self.verbindung:
            self.verbindung.executemany(sql, parameterliste)

    @contextmanager
    def transaktion(self):
        """Klammert mehrere Schreibbefehle zu einem einzigen Vorgang.

        Wird innerhalb des ``with``-Blocks ein Fehler ausgeloest, macht SQLite
        alle Aenderungen rueckgaengig. Genau so verlangt es /NF30/ fuer den
        Kassiervorgang: entweder Bestellung *und* Positionen *und* Lagerabgang
        werden gespeichert - oder gar nichts.

        Benutzung::

            with datenbank.transaktion() as verbindung:
                verbindung.execute(...)
                verbindung.execute(...)
        """
        try:
            yield self.verbindung
            self.verbindung.commit()
        except Exception:
            self.verbindung.rollback()
            raise

    # -- Aufraeumen --------------------------------------------------------

    def schliessen(self) -> None:
        """Schliesst die Verbindung (beim Beenden des Programms)."""
        self.verbindung.close()

    def __repr__(self) -> str:
        return f"<Datenbank pfad={self.pfad}>"


def datenbank_vorbereiten(pfad: Path | str | None = None) -> Datenbank:
    """Baut die Verbindung auf, legt das Schema an und liefert die Datenbank.

    Das ist die Funktion, die beim Programmstart (main.py) aufgerufen wird.
    """
    datenbank = Datenbank(pfad)
    datenbank.schema_anlegen()
    return datenbank
