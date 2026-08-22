"""Gemeinsame Basisklasse aller Repositories.

Ein *Repository* ist die Schicht zwischen Datenbank und Geschaeftslogik
(im Pflichtenheft "Data Access Object" genannt, Meilenstein 1). Es ist die
einzige Stelle, an der SQL steht. Wer die Datenbank spaeter austauschen wollte,
muesste nur diese Klassen anfassen.

Alle Repositories erben von ``BasisRepository`` und bekommen dadurch die
immer gleichen Methoden (``anzahl``, ``existiert``, ``loeschen``) geschenkt -
ein zweites Beispiel fuer Vererbung neben der Artikelhierarchie (/NF20/).
"""

from fanshop.datenbank.verbindung import Datenbank


class BasisRepository:
    """Basisklasse: kennt ihre Tabelle und ihren Primaerschluessel."""

    #: Name der Tabelle - wird von jeder Unterklasse gesetzt.
    tabelle: str = ""
    #: Name der Primaerschluesselspalte - wird von jeder Unterklasse gesetzt.
    schluessel: str = ""

    def __init__(self, datenbank: Datenbank) -> None:
        self.datenbank = datenbank

    def anzahl(self) -> int:
        """Anzahl aller Datensaetze der Tabelle.

        Wird auf der Berichtsseite fuer die Stammdatenzeile benutzt.
        """
        zeile = self.datenbank.abfragen_eine(f"SELECT COUNT(*) AS n FROM {self.tabelle}")
        return zeile["n"] if zeile else 0

    def existiert(self, schluesselwert: int) -> bool:
        """Prueft, ob ein Datensatz mit dieser ID vorhanden ist."""
        zeile = self.datenbank.abfragen_eine(
            f"SELECT 1 FROM {self.tabelle} WHERE {self.schluessel} = ?",
            (schluesselwert,),
        )
        return zeile is not None

    # Absichtlich gibt es hier **kein** allgemeines loeschen(). Artikel werden
    # deaktiviert statt geloescht (/F22/), Kunden brauchen die Anonymisierung
    # ihrer Bestellungen (/F43/). Eine geerbte DELETE-Methode waere eine
    # Abkuerzung, die beide Regeln umgeht.

    def __repr__(self) -> str:
        return f"<{type(self).__name__} tabelle={self.tabelle}>"
