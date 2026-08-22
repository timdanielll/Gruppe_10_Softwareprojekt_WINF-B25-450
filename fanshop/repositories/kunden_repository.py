"""Datenzugriff fuer Kunden (/F41/ bis /F44/, /F52/, /F53/)."""

from fanshop.modelle.kunde import Kunde
from fanshop.repositories.basis_repository import BasisRepository

SPALTEN = "name, strasse, plz, ort, newsletter_aktiv, newsletter_rabatt_verfuegbar, sticker_kontostand"
PLATZHALTER = ", ".join("?" * 7)


class KundenRepository(BasisRepository):
    """Liest und schreibt Kunden."""

    tabelle = "kunde"
    schluessel = "kundennummer"

    # -- /F42/ Anlegen -----------------------------------------------------

    def speichern(self, kunde: Kunde) -> int:
        """Legt einen Kunden an; die Kundennummer vergibt die Datenbank."""
        neue_nummer = self.datenbank.ausfuehren(
            f"INSERT INTO kunde ({SPALTEN}) VALUES ({PLATZHALTER})",
            kunde.als_datenbankwerte(),
        )
        kunde.kundennummer = neue_nummer
        return neue_nummer

    def aktualisieren(self, kunde: Kunde) -> None:
        """Schreibt die Stammdaten zurueck.

        **Ohne** ``sticker_kontostand``: Der Zaehler gehoert zum Sammelalbum
        und wird ausschliesslich beim Kauf hochgezaehlt (siehe
        ``BestellRepository.kauf_verbuchen``). Wuerde er hier mitgeschrieben,
        koennte ein veraltetes Kunde-Objekt den Zaehler zuruecksetzen und
        Album und Zaehler liefen auseinander.
        """
        self.datenbank.ausfuehren(
            """UPDATE kunde SET
                   name = ?, strasse = ?, plz = ?, ort = ?,
                   newsletter_aktiv = ?, newsletter_rabatt_verfuegbar = ?
               WHERE kundennummer = ?""",
            (
                kunde.name,
                kunde.strasse,
                kunde.plz,
                kunde.ort,
                1 if kunde.newsletter_aktiv else 0,
                1 if kunde.newsletter_rabatt_verfuegbar else 0,
                kunde.kundennummer,
            ),
        )

    # -- Lesen -------------------------------------------------------------

    def laden(self, kundennummer: int) -> Kunde | None:
        zeile = self.datenbank.abfragen_eine(
            "SELECT * FROM kunde WHERE kundennummer = ?", (kundennummer,)
        )
        return Kunde.aus_zeile(zeile) if zeile else None

    def alle(self) -> list[Kunde]:
        """Alle Kunden, alphabetisch (/F41/)."""
        zeilen = self.datenbank.abfragen("SELECT * FROM kunde ORDER BY name")
        return [Kunde.aus_zeile(zeile) for zeile in zeilen]

    def suchen(self, suchtext: str) -> list[Kunde]:
        """Sucht nach Name oder Kundennummer (/F44/).

        Ist der Suchtext eine Zahl, wird zusaetzlich die Kundennummer geprueft.
        """
        muster = f"%{suchtext.strip()}%"
        if suchtext.strip().isdigit():
            zeilen = self.datenbank.abfragen(
                """SELECT * FROM kunde
                   WHERE name LIKE ? OR kundennummer = ?
                   ORDER BY name""",
                (muster, int(suchtext.strip())),
            )
        else:
            zeilen = self.datenbank.abfragen(
                "SELECT * FROM kunde WHERE name LIKE ? ORDER BY name", (muster,)
            )
        return [Kunde.aus_zeile(zeile) for zeile in zeilen]

    # -- /F43/ Loeschen mit Anonymisierung ---------------------------------

    def loeschen_und_anonymisieren(self, kundennummer: int) -> None:
        """Loescht den Kunden, behaelt aber seine Bestellungen (/F43/).

        Die Bestellungen bekommen ``kundennummer = NULL``. Sie zaehlen damit
        weiterhin in jedem Umsatzbericht mit, lassen sich aber keiner Person
        mehr zuordnen. Beides zusammen ist eine untrennbare Aenderung und
        laeuft deshalb in einer Transaktion (/NF30/).
        """
        with self.datenbank.transaktion() as verbindung:
            verbindung.execute(
                "UPDATE bestellung SET kundennummer = NULL WHERE kundennummer = ?",
                (kundennummer,),
            )
            verbindung.execute(
                "DELETE FROM kunde WHERE kundennummer = ?", (kundennummer,)
            )

    # -- /F53/ Sticker-Sammelalbum -----------------------------------------

    def sticker_album(self, kundennummer: int) -> dict[str, int]:
        """Welche Motive besitzt der Kunde und wie oft?

        :return: Woerterbuch Motivschluessel -> Anzahl (nur vorhandene Motive)
        """
        zeilen = self.datenbank.abfragen(
            "SELECT motiv, anzahl FROM kunde_sticker WHERE kundennummer = ?",
            (kundennummer,),
        )
        return {zeile["motiv"]: zeile["anzahl"] for zeile in zeilen}

    # -- /F52/ Newsletter --------------------------------------------------

    def newsletter_setzen(self, kundennummer: int, angemeldet: bool) -> None:
        """Meldet einen Kunden zum Newsletter an oder ab (/F52/).

        Bei einer **Neuanmeldung** wird zugleich der einmalige 10-Prozent-
        Gutschein freigeschaltet. Eine Abmeldung nimmt einen noch nicht
        eingeloesten Gutschein wieder zurueck.
        """
        if angemeldet:
            self.datenbank.ausfuehren(
                """UPDATE kunde
                   SET newsletter_aktiv = 1,
                       newsletter_rabatt_verfuegbar = 1
                   WHERE kundennummer = ? AND newsletter_aktiv = 0""",
                (kundennummer,),
            )
        else:
            self.datenbank.ausfuehren(
                """UPDATE kunde
                   SET newsletter_aktiv = 0, newsletter_rabatt_verfuegbar = 0
                   WHERE kundennummer = ?""",
                (kundennummer,),
            )
