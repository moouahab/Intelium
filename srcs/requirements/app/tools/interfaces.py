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

    def write(self, results: list[dict], output_conf: dict | None = None) -> Path:
        ...


class CacheBackend(Protocol):
    """
    Interface minimale du cache (file/mongo/registry).
    """

    def get(self, url: str):
        ...

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: str | None = None,
        date: str | None = None,
        error: str | None = None,
        saved_path: str | None = None,
        extracted: list | None = None,
        keywords: dict | None = None,
    ):
        ...

    def has_changed(self, url: str, current_hash: str | None) -> bool:
        ...


class CacheStore(CacheBackend, Protocol):
    """
    Interface d'un cache administrable (stats/purge).
    """

    def stats(self) -> dict:
        ...

    def clear(self) -> dict:
        ...


class ResultStore(Protocol):
    """
    Interface de persistance des résultats.
    """

    def save(self, result: dict) -> None:
        ...
