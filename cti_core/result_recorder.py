import threading
from typing import Any
from tools.cache import CacheManager, CacheRegistry
from cti_core.Source import Source


class ResultRecorder:
    """
    Centralise l'écriture thread-safe des résultats et du cache.
    """

    def __init__(self, cache: CacheManager | CacheRegistry, results_store: list[dict[str, Any]]):
        self.cache = cache
        self.results = results_store
        self._lock = threading.Lock()

    def record_cache_hit(self, url: str, source_type: str, name: str, cached_entry) -> None:
        with self._lock:
            self.cache.record_scrape(
                url=url,
                source_type=source_type,
                status="skipped-cache",
                hash_value=cached_entry.hash,
                date=cached_entry.date,
                error=None,
                saved_path=cached_entry.saved_path,
            )
            self.results.append(
                {
                    "url": url,
                    "name": name,
                    "type": source_type,
                    "status": "skipped-cache",
                    "error": None,
                    "saved_path": cached_entry.saved_path,
                }
            )

    def record_result(self, source: Source, result, extracted, keyword_hits: dict | None = None) -> None:
        with self._lock:
            self.cache.record_scrape(
                url=source.url,
                source_type=source.type,
                status=result.status,
                hash_value=source.hash,
                date=source.date,
                error=result.error,
                saved_path=str(result.saved_path) if getattr(result, "saved_path", None) else None,
            )
            self.results.append(
                {
                    "url": source.url,
                    "name": source.name,
                    "type": source.type,
                    "status": result.status,
                    "error": result.error,
                    "saved_path": str(result.saved_path) if getattr(result, "saved_path", None) else None,
                    "extracted": extracted,
                    **({"keywords": keyword_hits} if keyword_hits else {}),
                }
            )

    def check_or_record_cache_hit(self, url: str, source_type: str, name: str) -> bool:
        """
        Retourne True si un cache hit est trouvé et enregistré.
        """
        cached = self.cache.get(url)
        if cached and cached.hash and cached.status == "downloaded":
            self.record_cache_hit(url, source_type, name, cached)
            return True
        return False
