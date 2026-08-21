"""Fachklassen fuer Artikel (Pflichtenheft Kapitel 6.2).

Hier steht das einzige Beispiel fuer echte Vererbung im Datenmodell (/NF20/):

    Artikel                 -> alle Produkte des Shops
      Kleidungsartikel      -> zusaetzlich das Merkmal "Groesse"

Das Lastenheft verlangt genau das: "Artikel haben in Abhaengigkeit ihrer
Kategorie weitere Merkmale (Herren / Damen, Groesse etc.)".
"""

import sqlite3

from fanshop import konfiguration
from fanshop.hilfsmittel import heute_iso, runde_geld


class Artikel:
    """Ein Produkt des WI Fanshops."""

    def __init__(
        self,
        titel: str,
        kategorie: str,
        preis: float,
        lagerbestand: int = 0,
        beschreibung: str = "",
        rabattsatz: float = 0.0,
        erstellungsdatum: str | None = None,
        aktiv: bool = True,
        bildpfad: str | None = None,
        artikel_id: int | None = None,
    ) -> None:
        self.artikel_id = artikel_id            # None = noch nicht gespeichert
        self.titel = titel
        self.kategorie = kategorie
        self.beschreibung = beschreibung
        self.preis = preis
        self.rabattsatz = rabattsatz            # 0.15 = 15 Prozent
        self.lagerbestand = lagerbestand
        self.erstellungsdatum = erstellungsdatum or heute_iso()
        self.aktiv = aktiv
        self.bildpfad = bildpfad

    # -- berechnete Werte --------------------------------------------------

    @property
    def endpreis(self) -> float:
        """Einzelpreis nach Abzug des artikeleigenen Rabatts."""
        return runde_geld(self.preis * (1 - self.rabattsatz))

    @property
    def hat_rabatt(self) -> bool:
        return self.rabattsatz > 0

    @property
    def ist_verfuegbar(self) -> bool:
        return self.aktiv and self.lagerbestand > 0

    def merkmale(self) -> str:
        """Zusaetzliche Eigenschaften als Text.

        Die Basisklasse hat keine - Unterklassen ueberschreiben diese Methode
        (Polymorphie). Die GUI ruft immer nur ``artikel.merkmale()`` auf und
        muss nicht wissen, um welche Artikelart es sich handelt.
        """
        return ""

    # -- Umwandlung Datenbank <-> Objekt -----------------------------------

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Artikel":
        """Erzeugt aus einer Datenbankzeile das passende Artikelobjekt.

        Diese Methode entscheidet, welche Klasse benutzt wird: Artikel der
        Kategorien "Damen" und "Herren" werden zu ``Kleidungsartikel``,
        alle anderen zu ``Artikel``. Man nennt so etwas eine Fabrikmethode.
        """
        gemeinsam = dict(
            artikel_id=zeile["artikel_id"],
            titel=zeile["titel"],
            kategorie=zeile["kategorie"],
            beschreibung=zeile["beschreibung"] or "",
            preis=zeile["preis"],
            rabattsatz=zeile["rabattsatz"],
            lagerbestand=zeile["lagerbestand"],
            erstellungsdatum=zeile["erstellungsdatum"],
            aktiv=bool(zeile["aktiv"]),
            bildpfad=zeile["bildpfad"],
        )
        if zeile["kategorie"] in konfiguration.KLEIDUNGS_KATEGORIEN:
            return Kleidungsartikel(groesse=zeile["groesse"] or "", **gemeinsam)
        return Artikel(**gemeinsam)

    def groesse_wert(self) -> str | None:
        """Wert fuer die Spalte ``groesse``.

        Ein normaler Artikel hat keine Groesse; ``Kleidungsartikel``
        ueberschreibt diese Methode.
        """
        return None

    def als_datenbankwerte(self) -> tuple:
        """Alle Felder in genau der Reihenfolge, in der sie gespeichert werden."""
        return (
            self.kategorie,
            self.titel,
            self.beschreibung,
            self.preis,
            self.rabattsatz,
            self.lagerbestand,
            self.erstellungsdatum,
            1 if self.aktiv else 0,
            self.groesse_wert(),
            self.bildpfad,
        )

    # -- Darstellung -------------------------------------------------------

    def __str__(self) -> str:
        return f"{self.titel} ({self.kategorie})"

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.artikel_id} {self.titel!r}>"


class Kleidungsartikel(Artikel):
    """Artikel der Kategorien Damen und Herren - hat zusaetzlich eine Groesse."""

    def __init__(self, *args, groesse: str = "", **kwargs) -> None:
        super().__init__(*args, **kwargs)       # alles Gemeinsame erledigt die Basisklasse
        self.groesse = groesse

    def merkmale(self) -> str:
        """Ueberschreibt die Basisklasse: gibt die Groesse aus."""
        return f"Größe: {self.groesse}" if self.groesse else ""

    def groesse_wert(self) -> str | None:
        """Ueberschreibt die Basisklasse: speichert die Groesse mit ab."""
        return self.groesse or None

    def __str__(self) -> str:
        if self.groesse:
            return f"{self.titel} ({self.kategorie}, Gr. {self.groesse})"
        return super().__str__()
