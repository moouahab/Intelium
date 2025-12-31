import threading
from typing import Any
from tools.cache import CacheManager, CacheRegistry
from cti_core.Source import Source
from tools.storage_mongo import save_result
from tools.scorer import compute_confidence


class ResultRecorder:
    """
    Centralise l'écriture thread-safe des résultats et du cache.
    """

    def __init__(self, cache: CacheManager | CacheRegistry, results_store: list[dict[str, Any]]):
        self.cache = cache
        self.results = results_store
        self._lock = threading.Lock()

    def record_cache_hit(self, source: Source, cached_entry, extracted=None, keyword_hits=None) -> None:
        with self._lock:
            self.cache.record_scrape(
                url=source.url,
                source_type=source.type,
                status="skipped-cache",
                hash_value=cached_entry.hash,
                date=cached_entry.date,
                error=None,
                saved_path=cached_entry.saved_path,
            )
            self.results.append(
                {
                    "url": source.url,
                    "name": source.name,
                    "type": source.type,
                    "status": "skipped-cache",
                    "error": None,
                    "saved_path": cached_entry.saved_path,
                    "extracted": extracted or [],
                    "confidence": compute_confidence(
                        {"status": "skipped-cache", "extracted": extracted or [], "keywords": keyword_hits or {}}
                    ),
                    **({"keywords": keyword_hits} if keyword_hits else {}),
                }
            )
            record = self.results[-1]
            try:
                save_result(record)
            except Exception:
                pass

    def record_result(self, source: Source, result, extracted, keyword_hits: dict | None = None) -> None:
        with self._lock:
            saved_path = str(result.saved_path) if getattr(result, "saved_path", None) else None
            conf = compute_confidence({"status": result.status, "extracted": extracted, "keywords": keyword_hits or {}})
            self.cache.record_scrape(
                url=source.url,
                source_type=source.type,
                status=result.status,
                hash_value=source.hash,
                date=source.date,
                error=result.error,
                saved_path=saved_path,
                extracted=extracted,
                keywords=keyword_hits,
            )
            record = {
                "url": source.url,
                "name": source.name,
                "type": source.type,
                "status": result.status,
                "error": result.error,
                "saved_path": saved_path,
                "extracted": extracted,
                "confidence": conf,
            }
            if keyword_hits:
                record["keywords"] = keyword_hits
            self.results.append(record)
            try:
                save_result(record)
            except Exception:
                pass

    def check_or_record_cache_hit(self, url: str, source_type: str, name: str) -> bool:
        """Deprecated: use record_cache_hit with a Source object."""
        return False
