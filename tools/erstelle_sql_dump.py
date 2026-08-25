"""Erzeugt den für die Abgabe benötigten SQL-Dump der Fanshop-Datenbank.

Aufruf aus dem Projektverzeichnis:

    python tools/erstelle_sql_dump.py

Optional können Quelle und Ziel angegeben werden:

    python tools/erstelle_sql_dump.py --quelle andere.db --ziel docs/fanshop_dump.sql
"""

import argparse
import sqlite3
from pathlib import Path


PROJEKT_VERZEICHNIS = Path(__file__).resolve().parent.parent
STANDARD_QUELLE = PROJEKT_VERZEICHNIS / "fanshop.db"
STANDARD_ZIEL = PROJEKT_VERZEICHNIS / "docs" / "fanshop_dump.sql"


def sql_dump_erzeugen(quelle: Path, ziel: Path) -> None:
    """Schreibt einen SQLite-kompatiblen Dump von *quelle* nach *ziel*."""
    if not quelle.is_file():
        raise FileNotFoundError(f"Datenbank nicht gefunden: {quelle}")

    ziel.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(quelle) as datenbank:
        zeilen = datenbank.iterdump()
        inhalt = "\n".join(zeilen)

    kopf = (
        "-- WI Fanshop: SQL-Dump für die Abgabe\n"
        "-- Erzeugt mit tools/erstelle_sql_dump.py aus fanshop.db.\n"
        "-- Import: sqlite3 neue_datenbank.db < docs/fanshop_dump.sql\n\n"
    )
    ziel.write_text(kopf + inhalt + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Erzeugt einen SQLite-SQL-Dump.")
    parser.add_argument("--quelle", type=Path, default=STANDARD_QUELLE)
    parser.add_argument("--ziel", type=Path, default=STANDARD_ZIEL)
    argumente = parser.parse_args()

    quelle = argumente.quelle.resolve()
    ziel = argumente.ziel.resolve()
    sql_dump_erzeugen(quelle, ziel)
    print(f"SQL-Dump erstellt: {ziel}")


if __name__ == "__main__":
    main()
