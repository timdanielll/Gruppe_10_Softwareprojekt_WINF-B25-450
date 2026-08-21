"""Das Sticker-Sammelsystem (/F53/).

Der Fanshop legt sechs verschiedene Stickermotive bei. Bei jedem Einkauf
bekommt der Kunde **drei davon** - nicht dreimal dasselbe. Genau das macht aus
einer Zahl auf dem Konto eine Sammlung, und genau darum geht es beim
Gamification-Modul aus dem Pflichtenheft.

Welche drei Motive es sind, wird **nicht ausgelost**, sondern der Reihe nach
vergeben: Wer schon vier Sticker hat, bekommt als Nächstes Motiv 5, 6 und
wieder 1. Zwei Vorteile:

* Nach zwei Einkäufen ist das Album garantiert einmal komplett - der Kunde
  bekommt nie dreimal dasselbe Motiv hintereinander.
* Das Verhalten ist wiederholbar und damit testbar. Ein Zufallsgenerator
  würde jeden Test unzuverlässig machen.
"""

from fanshop import konfiguration


class Stickermotiv:
    """Ein Sammelmotiv: Dateiname plus Anzeigetitel."""

    def __init__(self, schluessel: str, titel: str, datei: str) -> None:
        self.schluessel = schluessel      # so steht es in der Datenbank
        self.titel = titel                # so steht es in der Oberflaeche
        self.datei = datei                # Dateiname in assets/sticker/

    @property
    def pfad(self):
        """Vollstaendiger Pfad zur Bilddatei."""
        return konfiguration.STICKER_VERZEICHNIS / self.datei

    def __str__(self) -> str:
        return self.titel

    def __repr__(self) -> str:
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

    :param bisheriger_kontostand: wie viele Sticker der Kunde schon hat
    :param anzahl: wie viele Sticker es diesmal gibt (Standard: 3, /F53/)
    :return: Liste der Motive, in der Reihenfolge der Ausgabe
    """
    if anzahl is None:
        anzahl = konfiguration.STICKER_PRO_EINKAUF

    start = bisheriger_kontostand % len(MOTIVE)
    return [MOTIVE[(start + schritt) % len(MOTIVE)] for schritt in range(anzahl)]


def album_fortschritt(album: dict[str, int]) -> tuple[int, int]:
    """Wie viele der sechs Motive besitzt der Kunde schon?

    :param album: Woerterbuch Motivschluessel -> Anzahl
    :return: (verschiedene Motive, Gesamtzahl der Motive)
    """
    verschieden = sum(1 for anzahl in album.values() if anzahl > 0)
    return verschieden, len(MOTIVE)
