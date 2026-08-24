"""Datenzugriff fuer Sonderaktionen."""

from fanshop.modelle.sonderaktion import Sonderaktion
from fanshop.repositories.basis_repository import BasisRepository


class SonderaktionRepository(BasisRepository):
    """Liest und schreibt die fest definierten Spezialangebote."""

    tabelle = "sonderaktion"
    schluessel = "aktions_id"

    def speichern(self, aktion: Sonderaktion) -> int:
        """Legt eine Sonderaktion an und gibt ihre Nummer zurueck."""
        neue_id = self.datenbank.ausfuehren(
            """INSERT INTO sonderaktion
                   (titel, art, zielkategorie, mindestbestellwert, rabattsatz, aktiv)
               VALUES (?, ?, ?, ?, ?, ?)""",
            aktion.als_datenbankwerte(),
        )
        aktion.aktions_id = neue_id
        return neue_id

    def alle(self) -> list[Sonderaktion]:
        """Alle hinterlegten Aktionen, aktive zuerst."""
        zeilen = self.datenbank.abfragen("SELECT * FROM sonderaktion ORDER BY aktions_id")
        return [Sonderaktion.aus_zeile(zeile) for zeile in zeilen]

    def aktive(self) -> Sonderaktion | None:
        """Die eine gerade aktive Aktion - oder None.

        Es kann immer nur eine Aktion aktiv sein; darum sorgt :meth:`aktivieren`.
        """
        zeile = self.datenbank.abfragen_eine(
            "SELECT * FROM sonderaktion WHERE aktiv = 1 LIMIT 1"
        )
        return Sonderaktion.aus_zeile(zeile) if zeile else None

    def aktivieren(self, aktions_id: int) -> None:
        """Schaltet genau eine Aktion scharf und alle anderen ab."""
        with self.datenbank.transaktion() as verbindung:
            verbindung.execute("UPDATE sonderaktion SET aktiv = 0")
            verbindung.execute(
                "UPDATE sonderaktion SET aktiv = 1 WHERE aktions_id = ?", (aktions_id,)
            )

    def alle_deaktivieren(self) -> None:
        """Beendet jede laufende Aktion."""
        self.datenbank.ausfuehren("UPDATE sonderaktion SET aktiv = 0")
