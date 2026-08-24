"""Fachklassen fuer Artikel (Pflichtenheft Kapitel 6.2).

Hier steht das einzige Beispiel fuer echte Vererbung im Datenmodell (/NF20/):

    Artikel                 -> alle Produkte des Shops
      Kleidungsartikel      -> zusaetzlich das Merkmal "Groessen"

Das Lastenheft verlangt genau das: "Artikel haben in Abhaengigkeit ihrer
Kategorie weitere Merkmale (Herren / Damen, Groesse etc.)".

Wichtig zur Groesse: Ein Kleidungsstueck steht **einmal** im Sortiment und ist
in allen Groessen seiner Kategorie zu haben (Damen S-XL, Herren S-5XL). Welche
Groesse es sein soll, entscheidet sich erst beim Bestellen - die Auswahl steht
deshalb im Warenkorb (``modelle/warenkorb.py``) und auf der Bestellposition,
nicht am Artikel.
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
        """Legt einen Artikel mit allen Stammdaten an."""
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
        """True, wenn auf diesen Artikel ein eigener Rabatt liegt."""
        return self.rabattsatz > 0

    @property
    def ist_verfuegbar(self) -> bool:
        """True, wenn der Artikel verkauft wird und noch auf Lager ist."""
        return self.aktiv and self.lagerbestand > 0

    @property
    def groessen(self) -> tuple[str, ...]:
        """Waehlbare Groessen - bei einem normalen Artikel keine.

        ``Kleidungsartikel`` ueberschreibt das. Die GUI fragt immer nur
        ``artikel.groessen`` und muss die Artikelart nicht kennen.
        """
        return ()

    @property
    def braucht_groesse(self) -> bool:
        """True, wenn beim Bestellen eine Groesse gewaehlt werden muss."""
        return bool(self.groessen)

    def merkmale(self) -> str:
        """Zusaetzliche Eigenschaften als Text.

        Die Basisklasse hat keine - Unterklassen ueberschreiben diese Methode
        (Polymorphie). Die GUI ruft immer nur ``artikel.merkmale()`` auf und
        muss nicht wissen, um welche Artikelart es sich handelt.
        """
        return ""

    def groesse_pruefen(self, groesse: str) -> str:
        """Prueft eine gewaehlte Groesse und liefert den zu speichernden Wert.

        Ein Artikel ohne Groessen nimmt keine an; ``Kleidungsartikel``
        ueberschreibt diese Methode und verlangt eine gueltige.
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
            return Kleidungsartikel(**gemeinsam)
        return Artikel(**gemeinsam)

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
            self.bildpfad,
        )

    # -- Darstellung -------------------------------------------------------

    def __str__(self) -> str:
        """Titel und Kategorie - so steht der Artikel in Listen."""
        return f"{self.titel} ({self.kategorie})"

    def __repr__(self) -> str:
        """Kurzform fuer die Fehlersuche."""
        return f"<{type(self).__name__} {self.artikel_id} {self.titel!r}>"


class Kleidungsartikel(Artikel):
    """Artikel der Kategorien Damen und Herren - in mehreren Groessen zu haben.

    Welche Groessen das sind, haengt allein an der Kategorie und steht in
    ``konfiguration.GROESSEN_JE_KATEGORIE``. Damit fuehren Damen und Herren
    dasselbe Sortiment, nur eben in unterschiedlichen Spannen.
    """

    @property
    def groessen(self) -> tuple[str, ...]:
        """Ueberschreibt die Basisklasse: die Groessen dieser Kategorie."""
        return konfiguration.groessen_fuer(self.kategorie)

    def merkmale(self) -> str:
        """Ueberschreibt die Basisklasse: gibt die Groessenspanne aus."""
        if not self.groessen:
            return ""
        return f"Größen: {', '.join(self.groessen)}"

    def groesse_pruefen(self, groesse: str) -> str:
        """Ueberschreibt die Basisklasse: nimmt nur Groessen dieser Kategorie an.

        :raises ValidierungsFehler: wenn nichts oder etwas Unbekanntes gewaehlt wurde
        """
        from fanshop.fehler import ValidierungsFehler

        gewaehlt = (groesse or "").strip().upper()
        if not gewaehlt:
            raise ValidierungsFehler(
                f"Für „{self.titel}“ bitte eine Größe wählen "
                f"({', '.join(self.groessen)})."
            )
        if gewaehlt not in self.groessen:
            raise ValidierungsFehler(
                f"Größe „{groesse}“ gibt es für „{self.titel}“ nicht. "
                f"Möglich sind: {', '.join(self.groessen)}."
            )
        return gewaehlt

    def __str__(self) -> str:
        """Titel, Kategorie und Groessenspanne."""
        if self.groessen:
            return f"{self.titel} ({self.kategorie}, {self.groessen[0]}–{self.groessen[-1]})"
        return super().__str__()
