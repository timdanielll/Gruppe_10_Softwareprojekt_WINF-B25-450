"""Repositories: der einzige Ort im Programm, an dem SQL steht.

Jedes Repository gehoert zu einer Tabelle und wandelt zwischen Datenbankzeilen
und Fachklassen um. Alle erben von ``BasisRepository``.
"""

from fanshop.repositories.artikel_repository import ArtikelRepository
from fanshop.repositories.basis_repository import BasisRepository
from fanshop.repositories.bericht_repository import BerichtRepository
from fanshop.repositories.bestell_repository import BestellRepository
from fanshop.repositories.kunden_repository import KundenRepository
from fanshop.repositories.sonderaktion_repository import SonderaktionRepository

__all__ = [
    "BasisRepository",
    "ArtikelRepository",
    "KundenRepository",
    "BestellRepository",
    "BerichtRepository",
    "SonderaktionRepository",
]
