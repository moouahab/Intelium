from __future__ import annotations

from pathlib import Path
from typing import Protocol, Any, Optional


class GenericFetcher(Protocol):
    """
    Interface minimale d'un fetcher : un objet qui sait récupérer une source.
    """

    def fetch(self, source: dict, storage: Any | None = None) -> Any:
        ...


class AIProvider(Protocol):
    """
    Interface d'un fournisseur IA : doit générer un rapport et retourner le chemin de sortie.
    """

    def generate(self, results: list[dict], ai_conf: dict, logger=None) -> Optional[Path]:
        ...


class Reporter(Protocol):
    """
    Interface d'un reporter : écrit un rapport principal (et éventuellement des détails) et retourne le chemin principal.
    """

    def write(self, results: list[dict], output_conf: dict) -> Path:
        ...
