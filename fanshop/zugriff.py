"""Zugriffsregeln für die Bereiche der Anwendung.

Das Modul kennt keine Oberfläche. Dadurch kann die Einschränkung auch ohne
ein geöffnetes Fenster automatisiert geprüft werden.
"""

SEITEN_NACH_ROLLE = {
    "kunde": ("kasse",),
    "kassierer": ("kasse", "artikel", "kunden", "retouren", "berichte"),
}


def erlaubte_seiten(rolle: str) -> tuple[str, ...]:
    """Liefert die Seiten, die für eine Rolle aufgebaut werden dürfen."""
    try:
        return SEITEN_NACH_ROLLE[rolle]
    except KeyError as fehler:
        raise ValueError(f"Unbekannte Rolle: {rolle}") from fehler

