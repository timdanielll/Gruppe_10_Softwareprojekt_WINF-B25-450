"""Das Starterset - das Sonderangebot zur vollen Stickersammlung (/F53/).

Das Sammelsystem gibt pro Einkauf zwei von sechs Motiven aus, jedes genau
einmal. Nach dem **dritten** Einkauf ist die Sammlung damit vollstaendig - und
genau dann greift dieses Sonderangebot: Der Kunde bekommt einmalig ein
Starterset aus **Stift, Block und Jutebeutel** gratis dazu. Es wird seinem
Kundenkonto gutgeschrieben und der Bestellung beigelegt.

Warum ein eigenes Modul und keine ``Sonderaktion``?
---------------------------------------------------
Eine ``Sonderaktion`` ist ein **Rabattsatz**, den der Bediener scharf schaltet,
und es darf immer nur eine gleichzeitig laufen (siehe
``modelle/sonderaktion.py``). Das Starterset ist beides nicht: Es ist keine
Preisminderung, sondern eine Sachpraemie, und es ist ein **Dauerangebot** - es
soll nicht verschwinden, nur weil jemand nebenbei "20 % auf Schreibwaren"
startet. Deshalb steht es hier als eigene Fachregel und wird in der Oberflaeche
zusaetzlich unter den Sonderaktionen als dauerhaftes Sonderangebot angezeigt.

Drei Bedingungen, alle drei muessen erfuellt sein
--------------------------------------------------
1. Es gibt ueberhaupt ein Kundenkonto (Laufkundschaft geht leer aus).
2. Der Kunde hat mindestens ``STARTERSET_MINDESTBESTELLUNGEN`` Einkaeufe
   abgeschlossen - diesen mitgezaehlt.
3. Seine Sammlung ist vollstaendig (alle sechs Motive).

Und eine Sperre: ``bereits_erhalten`` verhindert, dass jemand das Set ein
zweites Mal bekommt. Einmal pro Kunde, nicht einmal pro Bestellung.

Einen Mindestbestellwert gibt es bewusst nicht - es zaehlt allein, wie oft
jemand eingekauft hat.
"""

from fanshop import konfiguration
from fanshop.modelle import sticker as sticker_modell

#: Was im Set steckt - Reihenfolge wie auf dem Beipackzettel.
INHALT: tuple[str, ...] = konfiguration.STARTERSET_INHALT

#: Anzeigename des Sonderangebots.
TITEL: str = konfiguration.STARTERSET_TITEL

#: So viele abgeschlossene Einkaeufe braucht es.
MINDESTBESTELLUNGEN: int = konfiguration.STARTERSET_MINDESTBESTELLUNGEN


def inhalt_text() -> str:
    """Der Inhalt als Aufzaehlung: 'Stift, Block und Jutebeutel'."""
    if len(INHALT) == 1:
        return INHALT[0]
    return f"{', '.join(INHALT[:-1])} und {INHALT[-1]}"


def bedingung_text() -> str:
    """Die Bedingung in einem Satz - fuer Oberflaeche und Dokumentation."""
    return (
        f"ab {MINDESTBESTELLUNGEN} Einkäufen mit vollständiger Stickersammlung, "
        f"einmalig je Kunde"
    )


def anspruch_besteht(
    anzahl_bestellungen: int,
    album: dict[str, int],
    bereits_erhalten: bool = False,
) -> bool:
    """Hat der Kunde jetzt Anspruch auf das Starterset?

    :param anzahl_bestellungen: abgeschlossene Einkaeufe **einschliesslich**
                                des gerade gebuchten
    :param album: Sammelalbum nach diesem Kauf (Motivschluessel -> Anzahl)
    :param bereits_erhalten: True, wenn der Kunde das Set schon einmal bekam
    :return: True, wenn das Set diesem Kauf beizulegen ist
    """
    if bereits_erhalten:
        return False
    if anzahl_bestellungen < MINDESTBESTELLUNGEN:
        return False
    return sticker_modell.album_vollstaendig(album)


def fehlende_bestellungen(anzahl_bestellungen: int) -> int:
    """Wie viele Einkaeufe fehlen noch bis zur Bedingung? (0 = erfuellt)"""
    return max(MINDESTBESTELLUNGEN - anzahl_bestellungen, 0)
