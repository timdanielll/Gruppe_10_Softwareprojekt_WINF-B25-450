"""Fachklassen (Modelle) des WI Fanshop.

Diese Klassen enthalten die Daten und die Regeln, die unmittelbar zu den Daten
gehoeren - zum Beispiel "Endpreis = Preis minus Rabatt". Sie wissen nichts von
SQL und nichts von der Oberflaeche.

Damit man ueberall kurz schreiben kann::

    from fanshop.modelle import Artikel, Kunde, Warenkorb
"""

from fanshop.modelle.artikel import Artikel, Kleidungsartikel
from fanshop.modelle.bestellung import Bestellposition, Bestellung
from fanshop.modelle.kunde import Kunde
from fanshop.modelle.retoure import Retoure
from fanshop.modelle.sonderaktion import Sonderaktion
from fanshop.modelle.sticker import MOTIVE, Stickermotiv, album_fortschritt, motive_fuer_kauf
from fanshop.modelle.warenkorb import Preisuebersicht, Warenkorb, WarenkorbPosition

__all__ = [
    "Artikel",
    "Kleidungsartikel",
    "Kunde",
    "Bestellung",
    "Bestellposition",
    "Retoure",
    "Sonderaktion",
    "Stickermotiv",
    "MOTIVE",
    "motive_fuer_kauf",
    "album_fortschritt",
    "Warenkorb",
    "WarenkorbPosition",
    "Preisuebersicht",
]
