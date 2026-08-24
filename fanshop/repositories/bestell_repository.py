"""Datenzugriff fuer Bestellungen, Bestellpositionen und Retouren.

Zwei Methoden dieser Klasse sind besonders wichtig, weil sie mehrere Tabellen
gleichzeitig veraendern und deshalb **eine einzige Transaktion** bilden
(/NF30/): ``kauf_verbuchen`` (/F14/) und ``retoure_verbuchen`` (/F51/).

Warum steht das hier und nicht in der Logikschicht? Weil "Bestellung schreiben,
Positionen schreiben, Lager abbuchen, Sticker gutschreiben" fuer die Datenbank
ein einziger Vorgang ist. Wuerde man das auf mehrere Repository-Aufrufe
verteilen, koennte nach einem Absturz die Bestellung existieren, das Lager aber
noch unveraendert sein. Genau das verbietet /NF30/.
"""

from fanshop.hilfsmittel import jetzt_iso, jetzt_zeitstempel, runde_geld
from fanshop.modelle.bestellung import Bestellposition, Bestellung
from fanshop.modelle.retoure import Retoure
from fanshop.repositories.basis_repository import BasisRepository


class BestellRepository(BasisRepository):
    """Liest und schreibt Bestellungen, Positionen und Retouren."""

    tabelle = "bestellung"
    schluessel = "bestellnummer"

    # -- /F14/ Kauf abschliessen -------------------------------------------

    def kauf_verbuchen(
        self,
        kundennummer: int | None,
        positionen: list,
        gesamtbetrag: float,
        newsletter_rabatt_angewendet: bool,
        sticker: int = 0,
        sticker_motive: list[str] | None = None,
        starterset: bool = False,
    ) -> int:
        """Speichert einen abgeschlossenen Einkauf vollstaendig (/F14/).

        In **einer** Transaktion passiert alles Folgende oder nichts davon:

        1. Bestellung (= Rechnung) anlegen
        2. je Warenkorbposition eine Bestellposition anlegen
        3. Lagerbestand der gekauften Artikel reduzieren (Mitnahmemodus)
        4. dem Kunden Sticker gutschreiben (/F53/)
        5. das Starterset gutschreiben, wenn die Sammlung damit voll ist (/F53/)
        6. einen benutzten Newsletter-Gutschein als verbraucht markieren (/F52/)

        Zum gespeicherten Einzelpreis: In ``historischer_preis`` steht der
        Preis, den der Kunde **tatsaechlich** pro Stueck gezahlt hat. Rabatte
        auf den ganzen Warenkorb (Sonderaktion, Newsletter) werden dafuer
        gleichmaessig auf alle Positionen verteilt - sonst wuerde eine spaetere
        Retoure mehr Geld erstatten, als eingenommen wurde.

        :param positionen: Liste von ``WarenkorbPosition``
        :param sticker: wie viele Sticker gutgeschrieben werden. Muss zur
                        Laenge von ``sticker_motive`` passen - sonst laufen
                        Zaehler und Sammelalbum auseinander. Der KassenService
                        leitet beides aus derselben Motivliste ab, deshalb ist
                        der Standardwert hier bewusst 0 und nicht
                        ``STICKER_PRO_EINKAUF``.
        :param starterset: True, wenn dieser Bestellung das Starterset beiliegt
        :return: die vergebene Bestellnummer
        """
        zwischensumme = runde_geld(sum(p.zeilensumme for p in positionen))
        # Verteilungsfaktor: 1.0 wenn es keinen Warenkorbrabatt gab.
        faktor = (gesamtbetrag / zwischensumme) if zwischensumme > 0 else 1.0

        with self.datenbank.transaktion() as verbindung:
            # 1. Bestellung
            cursor = verbindung.execute(
                """INSERT INTO bestellung
                       (kundennummer, zeitstempel, gesamtbetrag,
                        newsletter_rabatt_angewendet, sticker_ausgegeben,
                        starterset_ausgegeben)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    kundennummer,
                    jetzt_zeitstempel(),
                    gesamtbetrag,
                    1 if newsletter_rabatt_angewendet else 0,
                    sticker,
                    1 if starterset else 0,
                ),
            )
            bestellnummer = cursor.lastrowid

            for position in positionen:
                gezahlter_einzelpreis = runde_geld(position.einzelpreis * faktor)

                # 2. Bestellposition
                verbindung.execute(
                    """INSERT INTO bestellposition
                           (bestellnummer, artikel_id, menge, historischer_preis)
                       VALUES (?, ?, ?, ?)""",
                    (
                        bestellnummer,
                        position.artikel.artikel_id,
                        position.menge,
                        gezahlter_einzelpreis,
                    ),
                )

                # 3. Lager abbuchen
                verbindung.execute(
                    """UPDATE artikel
                       SET lagerbestand = lagerbestand - ?
                       WHERE artikel_id = ?""",
                    (position.menge, position.artikel.artikel_id),
                )

            if kundennummer is not None:
                # 4. Sticker gutschreiben - Zaehler und Sammelalbum
                verbindung.execute(
                    """UPDATE kunde
                       SET sticker_kontostand = sticker_kontostand + ?
                       WHERE kundennummer = ?""",
                    (sticker, kundennummer),
                )
                for motiv in sticker_motive or []:
                    # Jedes Motiv gibt es nur einmal: "DO NOTHING" laesst eine
                    # bereits vorhandene Zeile unveraendert, statt sie
                    # hochzuzaehlen. Damit kann kein Sticker doppelt entstehen,
                    # selbst wenn die aufrufende Schicht sich irrt.
                    verbindung.execute(
                        """INSERT INTO kunde_sticker (kundennummer, motiv, anzahl)
                           VALUES (?, ?, 1)
                           ON CONFLICT (kundennummer, motiv) DO NOTHING""",
                        (kundennummer, motiv),
                    )

                # 5. Starterset gutschreiben - einmalig je Kunde (/F53/).
                # Die Bedingung "starterset_erhalten = 0" ist die eigentliche
                # Sperre: Selbst zwei gleichzeitige Kaeufe koennten das Set so
                # nur ein einziges Mal vergeben.
                if starterset:
                    verbindung.execute(
                        """UPDATE kunde
                           SET starterset_erhalten = 1
                           WHERE kundennummer = ? AND starterset_erhalten = 0""",
                        (kundennummer,),
                    )

                # 6. Newsletter-Gutschein verbrauchen
                if newsletter_rabatt_angewendet:
                    verbindung.execute(
                        """UPDATE kunde
                           SET newsletter_rabatt_verfuegbar = 0
                           WHERE kundennummer = ?""",
                        (kundennummer,),
                    )

        return bestellnummer

    # -- Bestellungen lesen ------------------------------------------------

    def anzahl_bestellungen(self, kundennummer: int) -> int:
        """Wie viele Einkaeufe hat dieser Kunde bisher abgeschlossen?

        Grundlage fuer das Starterset-Sonderangebot (/F53/): Es gibt das Set
        erst ab der dritten Bestellung. Geloeschte Kunden haben in ihren
        Bestellungen ``kundennummer = NULL`` und zaehlen deshalb hier nicht
        mehr mit (/F43/).
        """
        zeile = self.datenbank.abfragen_eine(
            "SELECT COUNT(*) AS anzahl FROM bestellung WHERE kundennummer = ?",
            (kundennummer,),
        )
        return zeile["anzahl"] if zeile else 0

    def laden(self, bestellnummer: int) -> Bestellung | None:
        """Laedt eine Bestellung samt ihrer Positionen."""
        zeile = self.datenbank.abfragen_eine(
            """SELECT b.*, k.name AS kundenname
               FROM bestellung b
               LEFT JOIN kunde k ON k.kundennummer = b.kundennummer
               WHERE b.bestellnummer = ?""",
            (bestellnummer,),
        )
        if zeile is None:
            return None

        bestellung = Bestellung.aus_zeile(zeile)
        bestellung.positionen = self.positionen_zu(bestellnummer)
        return bestellung

    def positionen_zu(self, bestellnummer: int) -> list[Bestellposition]:
        """Alle Positionen einer Bestellung, mit Artikeltitel fuer die Anzeige."""
        zeilen = self.datenbank.abfragen(
            """SELECT p.*, a.titel AS artikel_titel
               FROM bestellposition p
               JOIN artikel a ON a.artikel_id = p.artikel_id
               WHERE p.bestellnummer = ?
               ORDER BY p.position_id""",
            (bestellnummer,),
        )
        return [Bestellposition.aus_zeile(zeile) for zeile in zeilen]

    def letzte(self, anzahl: int = 50) -> list[Bestellung]:
        """Die neuesten Bestellungen - fuer die Uebersicht im Retourenterminal."""
        zeilen = self.datenbank.abfragen(
            """SELECT b.*, k.name AS kundenname
               FROM bestellung b
               LEFT JOIN kunde k ON k.kundennummer = b.kundennummer
               ORDER BY b.zeitstempel DESC
               LIMIT ?""",
            (anzahl,),
        )
        return [Bestellung.aus_zeile(zeile) for zeile in zeilen]

    # -- /F51/ Retouren ----------------------------------------------------

    def bereits_retourniert(self, bestellnummer: int, artikel_id: int) -> int:
        """Wie viele Stueck dieses Artikels wurden aus dieser Bestellung schon
        zurueckgegeben? Verhindert doppelte Erstattungen."""
        zeile = self.datenbank.abfragen_eine(
            """SELECT COALESCE(SUM(menge), 0) AS menge
               FROM retoure
               WHERE bestellnummer = ? AND artikel_id = ?""",
            (bestellnummer, artikel_id),
        )
        return zeile["menge"] if zeile else 0

    def retoure_verbuchen(
        self, bestellnummer: int, artikel_id: int, menge: int, historischer_preis: float
    ) -> Retoure:
        """Bucht eine Rueckgabe (/F51/).

        In einer Transaktion: Retourenbeleg schreiben **und** die Ware zurueck
        ins Lager buchen. Erstattet wird zum historischen Preis, also zu dem
        Betrag, den der Kunde damals wirklich gezahlt hat.
        """
        erstattungsbetrag = runde_geld(menge * historischer_preis)
        datum = jetzt_iso()

        with self.datenbank.transaktion() as verbindung:
            cursor = verbindung.execute(
                """INSERT INTO retoure
                       (bestellnummer, artikel_id, menge, retouren_datum, erstattungsbetrag)
                   VALUES (?, ?, ?, ?, ?)""",
                (bestellnummer, artikel_id, menge, datum, erstattungsbetrag),
            )
            retouren_id = cursor.lastrowid

            verbindung.execute(
                "UPDATE artikel SET lagerbestand = lagerbestand + ? WHERE artikel_id = ?",
                (menge, artikel_id),
            )

        return Retoure(
            retouren_id=retouren_id,
            bestellnummer=bestellnummer,
            artikel_id=artikel_id,
            menge=menge,
            erstattungsbetrag=erstattungsbetrag,
            retouren_datum=datum,
        )

    def retouren_zu(self, bestellnummer: int) -> list[Retoure]:
        """Alle bisherigen Retouren einer Bestellung."""
        zeilen = self.datenbank.abfragen(
            """SELECT r.*, a.titel AS artikel_titel
               FROM retoure r
               JOIN artikel a ON a.artikel_id = r.artikel_id
               WHERE r.bestellnummer = ?
               ORDER BY r.retouren_id""",
            (bestellnummer,),
        )
        return [Retoure.aus_zeile(zeile) for zeile in zeilen]
