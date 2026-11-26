import threading
from tools.interfaces import CacheBackend
from cti_core.Source import Source
from tools.providers.result_store import build_result_store, ResultStore
from tools.result_entry import ResultEntry
from tools.scorer import compute_confidence


class ResultRecorder:
    """
    Centralise l'écriture thread-safe des résultats et du cache.
    """

    def __init__(
        self,
        cache: CacheBackend,
        results_store: list[ResultEntry],
        result_store: ResultStore | None = None,
        run_meta: dict | None = None,
    ):
        self.cache = cache
        self.results = results_store
        self.result_store = result_store or build_result_store()
        self.run_meta = dict(run_meta or {})
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
                extracted=extracted,
                keywords=keyword_hits,
            )
            record = ResultEntry(
                url=source.url,
                name=source.name,
                type=source.type,
                status="skipped-cache",
                error=None,
                saved_path=cached_entry.saved_path,
                extracted=extracted or [],
                keywords=keyword_hits or None,
                confidence=compute_confidence(
                    {"status": "skipped-cache", "extracted": extracted or [], "keywords": keyword_hits or {}}
                ),
            )
            if self.run_meta:
                record.extra.update(self.run_meta)
            record.extra.update(retrieved_at=cached_entry.date, content_sha256=cached_entry.hash)
            self.results.append(record)
            self.result_store.save(record.to_dict())

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
            record = ResultEntry(
                url=source.url,
                name=source.name,
                type=source.type,
                status=result.status,
                error=result.error,
                saved_path=saved_path,
                extracted=extracted,
                keywords=keyword_hits or None,
                confidence=conf,
            )
            if self.run_meta:
                record.extra.update(self.run_meta)
            record.extra.update(retrieved_at=source.date, content_sha256=source.hash)
            self.results.append(record)
            self.result_store.save(record.to_dict())

    def check_or_record_cache_hit(self, url: str, source_type: str, name: str) -> bool:
        """Deprecated: use record_cache_hit with a Source object."""
        return False
