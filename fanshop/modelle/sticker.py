"""Das Sticker-Sammelsystem (/F53/).

Der Fanshop legt sechs verschiedene Stickermotive bei. Bei jedem Einkauf
bekommt der Kunde **zwei davon** - nicht zweimal dasselbe. Genau das macht aus
einer Zahl auf dem Konto eine Sammlung, und genau darum geht es beim
Gamification-Modul aus dem Pflichtenheft.

Drei Regeln bestimmen die Vergabe:

* **Feste Reihenfolge, kein Zufall.** Wer schon zwei Sticker hat, bekommt als
  Naechstes Motiv 3 und 4. Das ist wiederholbar und damit testbar; ein
  Zufallsgenerator wuerde jeden Test unzuverlaessig machen.
* **Jedes Motiv nur einmal.** Ein Sticker, den der Kunde schon besitzt, wird
  nie ein zweites Mal ausgegeben. Nach genau drei Einkaeufen ist die Sammlung
  voll - danach gibt es keine Sticker mehr, sondern das Starterset
  (siehe ``modelle/starterset.py``).
* **Kein Mindestbestellwert.** Jeder abgeschlossene Kauf zaehlt, unabhaengig
  vom Bestellwert. Nur Laufkundschaft ohne Kundenkonto geht leer aus - es gaebe
  niemanden, dem man die Sticker gutschreiben koennte.
"""

from fanshop import konfiguration


class Stickermotiv:
    """Ein Sammelmotiv: Dateiname plus Anzeigetitel."""

    def __init__(self, schluessel: str, titel: str, datei: str) -> None:
        """Legt ein Stickermotiv mit Schluessel, Titel und Bilddatei an."""
        self.schluessel = schluessel      # so steht es in der Datenbank
        self.titel = titel                # so steht es in der Oberflaeche
        self.datei = datei                # Dateiname in assets/sticker/

    @property
    def pfad(self):
        """Vollstaendiger Pfad zur Bilddatei."""
        return konfiguration.STICKER_VERZEICHNIS / self.datei

    def __str__(self) -> str:
        """Der Anzeigetitel des Motivs."""
        return self.titel

    def __repr__(self) -> str:
        """Kurzform fuer die Fehlersuche."""
        return f"<Stickermotiv {self.schluessel}>"


#: Die sechs Motive in fester Reihenfolge - sie bestimmt die Ausgabe.
MOTIVE: list[Stickermotiv] = [
    Stickermotiv("campus", "Campus Rotenbühl", "campus.png"),
    Stickermotiv("htwsaar", "Waren Sie schon an der htw saar?", "htwsaar.png"),
    Stickermotiv("kneipe", "Kneipentour", "kneipe.png"),
    Stickermotiv("liebt", "Wer liebt, der schiebt", "liebt.png"),
    Stickermotiv("mensen", "Erstmal mensen", "mensen.png"),
    Stickermotiv("vier", "Vier gewinnt", "vier.png"),
]

#: Nachschlagewerk Schluessel -> Motiv.
NACH_SCHLUESSEL = {motiv.schluessel: motiv for motiv in MOTIVE}


def motive_fuer_kauf(bisheriger_kontostand: int, anzahl: int | None = None) -> list[Stickermotiv]:
    """Welche Motive bekommt ein Kunde beim nächsten Einkauf?

    Die Vergabe laeuft die Liste ``MOTIVE`` von vorn nach hinten durch und
    **wiederholt sich nicht**: Wer schon vier Sticker hat, bekommt Motiv 5 und
    6 - und danach gar keine mehr.

    :param bisheriger_kontostand: wie viele Sticker der Kunde schon hat
    :param anzahl: wie viele Sticker es diesmal gibt (Standard: 2, /F53/)
    :return: Liste der Motive, in der Reihenfolge der Ausgabe; leer, sobald die
             Sammlung vollstaendig ist
    """
    if anzahl is None:
        anzahl = konfiguration.STICKER_PRO_EINKAUF

    # Negative oder zu grosse Kontostaende sollen die Liste nicht sprengen.
    bereits_vergeben = min(max(bisheriger_kontostand, 0), len(MOTIVE))
    return MOTIVE[bereits_vergeben:bereits_vergeben + max(anzahl, 0)]


def offene_motive(album: dict[str, int], anzahl: int | None = None) -> list[Stickermotiv]:
    """Welche Motive fehlen dem Kunden noch - hoechstens ``anzahl`` Stueck?

    Das ist die Vergabe, die beim echten Kauf benutzt wird. Sie fragt nicht den
    Zaehler, sondern das Album selbst - so kann selbst dann kein Motiv doppelt
    herausgehen, wenn Zaehler und Album einmal auseinanderlaufen sollten.

    :param album: Woerterbuch Motivschluessel -> Anzahl (nur besessene Motive)
    :param anzahl: wie viele Sticker es diesmal gibt (Standard: 2, /F53/)
    :return: die fehlenden Motive in der Reihenfolge von ``MOTIVE``
    """
    if anzahl is None:
        anzahl = konfiguration.STICKER_PRO_EINKAUF

    fehlend = [motiv for motiv in MOTIVE if album.get(motiv.schluessel, 0) <= 0]
    return fehlend[:max(anzahl, 0)]


def album_fortschritt(album: dict[str, int]) -> tuple[int, int]:
    """Wie viele der sechs Motive besitzt der Kunde schon?

    :param album: Woerterbuch Motivschluessel -> Anzahl
    :return: (verschiedene Motive, Gesamtzahl der Motive)
    """
    verschieden = sum(1 for anzahl in album.values() if anzahl > 0)
    return verschieden, len(MOTIVE)


def album_vollstaendig(album: dict[str, int]) -> bool:
    """True, wenn der Kunde alle sechs Motive besitzt - Bedingung fuers Starterset."""
    verschieden, gesamt = album_fortschritt(album)
    return verschieden >= gesamt
