"""Fachklasse fuer Sonderaktionen.

Das Lastenheft verlangt: "Es gibt fest (von Ihnen) definierte Spezialangebote,
die aktiviert werden koennen, d.h. spezielle Artikel sind reduziert oder ab
einem Mindestbestellwert gibt es Rabatte."

Daraus ergeben sich genau zwei Arten von Aktion:

* ``kategorie``   - alle Artikel einer Kategorie sind um X Prozent reduziert
* ``mindestwert`` - ab einem Bestellwert von Y Euro gibt es X Prozent auf alles

Es ist immer hoechstens **eine** Aktion gleichzeitig aktiv. Das haelt die
Rabattrechnung nachvollziehbar - und der Bediener kann dem Kunden erklaeren,
warum der Preis so ist, wie er ist.
"""

import sqlite3

from fanshop.fehler import ValidierungsFehler


class Sonderaktion:
    """Eine zeitweise aktivierbare Rabattaktion."""

    ART_KATEGORIE = "kategorie"
    ART_MINDESTWERT = "mindestwert"

    def __init__(
        self,
        titel: str,
        art: str,
        rabattsatz: float,
        zielkategorie: str | None = None,
        mindestbestellwert: float = 0.0,
        aktiv: bool = False,
        aktions_id: int | None = None,
    ) -> None:
        # Ohne diese Pruefung koennte eine Aktion mit rabattsatz >= 1.0 den
        # Gesamtbetrag negativ machen - der Shop wuerde Geld herausgeben.
        if not 0.0 <= rabattsatz < 1.0:
            raise ValidierungsFehler(
                "Der Rabattsatz einer Sonderaktion muss zwischen 0 % und 99 % liegen."
            )

        self.aktions_id = aktions_id
        self.titel = titel
        self.art = art
        self.rabattsatz = rabattsatz            # 0.20 = 20 Prozent
        self.zielkategorie = zielkategorie
        self.mindestbestellwert = mindestbestellwert
        self.aktiv = aktiv

    # -- fachliche Pruefungen ----------------------------------------------

    def gilt_fuer_artikel(self, artikel) -> bool:
        """True, wenn dieser Artikel von der Aktion betroffen ist."""
        return self.art == self.ART_KATEGORIE and artikel.kategorie == self.zielkategorie

    def gilt_fuer_bestellwert(self, zwischensumme: float) -> bool:
        """True, wenn die Aktion auf den gesamten Warenkorb wirkt."""
        return (
            self.art == self.ART_MINDESTWERT
            and zwischensumme >= self.mindestbestellwert
        )

    # -- Umwandlung Datenbank <-> Objekt -----------------------------------

    @classmethod
    def aus_zeile(cls, zeile: sqlite3.Row) -> "Sonderaktion":
        return cls(
            aktions_id=zeile["aktions_id"],
            titel=zeile["titel"],
            art=zeile["art"],
            rabattsatz=zeile["rabattsatz"],
            zielkategorie=zeile["zielkategorie"],
            mindestbestellwert=zeile["mindestbestellwert"],
            aktiv=bool(zeile["aktiv"]),
        )

    def als_datenbankwerte(self) -> tuple:
        return (
            self.titel,
            self.art,
            self.zielkategorie,
            self.mindestbestellwert,
            self.rabattsatz,
            1 if self.aktiv else 0,
        )

    def __str__(self) -> str:
        return self.titel
