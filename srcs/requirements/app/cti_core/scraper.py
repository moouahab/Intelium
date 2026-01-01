from typing import Set
from concurrent.futures import ThreadPoolExecutor

from .Source import Source
from .crawler_state import CrawlerState
from cti_core.sources_factory import enqueue_links
from cti_core.result_recorder import ResultRecorder
from tools.interfaces import CacheBackend
from tools.providers.http.download_types import NetworkPolicy
from tools.providers.http.url_utils import same_domain
from tools.parsing.extractor import Extractor
from tools.providers.fetchers import build_fetcher
from tools.providers.http.url_policy import UrlPolicy
from tools.parsers.text_utils import ensure_text
from tools.interfaces import GenericFetcher
from tools.quota import Quota
from tools.providers.http.download_types import DownloadResult
from tools.result_entry import ResultEntry
from pathlib import Path


class Scraper:
    def __init__(
        self,
        config_model,
        cache_manager: CacheBackend,
        http_client: GenericFetcher | None = None,
        extractor: Extractor | None = None,
        run_meta: dict | None = None,
    ):
        self.config_model = config_model
        self.cache = cache_manager
        self.results: list[ResultEntry] = []
        self.policy: NetworkPolicy = config_model.network_policy
        crawler_conf = config_model.crawler_settings
        self.max_depth = crawler_conf.get("max_depth", 2)
        self.max_pages = crawler_conf.get("max_pages")
        self.same_domain_only = bool(crawler_conf.get("same_domain_only", True))
        self.allow_domains: Set[str] = set(crawler_conf.get("allow_domains", []) or [])
        self.max_concurrent = int(crawler_conf.get("max_concurrent", 1) or 1)
        self.global_quota = Quota(
            max_pages=crawler_conf.get("global_max_pages"),
            max_bytes=crawler_conf.get("global_max_bytes"),
        )
        self.url_policy = UrlPolicy(
            same_domain_only=self.same_domain_only,
            allow_domains=self.allow_domains or None,
            normalizer_name=crawler_conf.get("url_normalizer", "strip"),
        )
        self.fetcher = build_fetcher(config_model, http_client=http_client)
        self.recorder = ResultRecorder(self.cache, self.results, run_meta=run_meta)
        self.extractor = extractor or Extractor(self.config_model.scraping_settings, getattr(self.config_model, "keywords", {}))

    def _normalize_url(self, url: str) -> str:
        return self.url_policy.normalize(url)

    def _same_domain(self, base: str, target: str) -> bool:
        return same_domain(base, target, self.allow_domains or None)

    def _fetch_and_parse(self, current: Source):
        storage = self.config_model.build_storage_target(current)
        source_dict = {"url": current.url, "type": current.type, "name": current.name}
        overrides = current.normalized_overrides() if hasattr(current, "normalized_overrides") else {}
        if overrides:
            source_dict["overrides"] = overrides

        result = self.fetcher.fetch(
            source_dict,
            storage=storage,
        )
        current.status = result.status
        current.error = result.error
        current.content = result.content
        if result.status == "downloaded":
            current.update_hash()

        extracted: list[str] = []
        keyword_hits: dict = {}
        if result.status == "downloaded":
            extracted, keyword_hits = self.extractor.extract(current.type, current.content, source_name=current.name)
        return result, extracted, keyword_hits

    def _parse_cached(self, current: Source, cached_entry):
        # Si on a déjà des extraits en cache (Mongo), on les réutilise en priorité
        if getattr(cached_entry, "extracted", None):
            return cached_entry.extracted, getattr(cached_entry, "keywords", {}) or {}
        if not cached_entry.saved_path:
            return [], {}
        path = Path(cached_entry.saved_path)
        if not path.exists():
            return [], {}
        try:
            raw_bytes = path.read_bytes()
        except Exception:
            return [], {}
        raw_content = raw_bytes
        if current.type in {"html", "api", "xml", "csv", "txt"}:
            raw_content = ensure_text(raw_bytes)
        extracted, keyword_hits = self.extractor.extract(current.type, raw_content, source_name=current.name)
        return extracted, keyword_hits

    def _process_source(self, state: CrawlerState, current: Source, depth: int) -> None:
        if state.already_visited(current.url):
            return
        state.mark_visited(current.url)

        cached = self.cache.get(current.url)
        if cached and cached.status == "downloaded":
            extracted, keyword_hits = self._parse_cached(current, cached)
            self.recorder.record_cache_hit(current, cached, extracted, keyword_hits)
            return
        if getattr(self.policy, "offline", False):
            from tools.providers.http.download_types import DownloadResult
            offline_result = DownloadResult(status="offline", content=None, error="Mode offline actif (cache manquant)")
            self.recorder.record_result(current, offline_result, [], {})
            return

        fetched = self._fetch_and_parse(current)
        if not isinstance(fetched, tuple):
            return
        if len(fetched) == 3:
            result, extracted, keyword_hits = fetched
        elif len(fetched) == 2:
            result, extracted = fetched
            keyword_hits = {}
        else:
            return

        self.recorder.record_result(current, result, extracted, keyword_hits)
        # Quota global de volume (optionnel)
        if self.global_quota:
            self.global_quota.add_bytes(getattr(result, "size_bytes", None))
        enqueue_links(
            current,
            depth,
            state,
            self.max_depth,
            self.url_policy,
        )

    def _worker_loop(self, state: CrawlerState):
        while True:
            item = state.pop_if_any()
            if not item:
                break
            current, depth = item
            if self.global_quota and not self.global_quota.reserve_page():
                # Limite globale atteinte, on marque la source et on arrête
                quota_result = DownloadResult(status="skipped-quota", content=None, error="Quota global atteint")
                self.recorder.record_result(current, quota_result, [], {})
                break
            self._process_source(state, current, depth)

    def _process_single(self, source: Source):
        thread_safe = self.max_concurrent > 1
        state = CrawlerState(self.max_depth, self.max_pages, self._normalize_url, thread_safe=thread_safe)
        state.add(source, 0)

        # Si le quota global de pages est déjà épuisé, on ne traite pas la source
        if self.global_quota and self.global_quota.max_pages is not None and self.global_quota.remaining_pages() == 0:
            quota_result = DownloadResult(status="skipped-quota", content=None, error="Quota global atteint")
            self.recorder.record_result(source, quota_result, [], {})
            return

        if self.max_concurrent <= 1:
            self._worker_loop(state)
        else:
            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                futures = [executor.submit(self._worker_loop, state) for _ in range(self.max_concurrent)]
                for future in futures:
                    future.result()

    def run(self):
        for source in self.config_model.source_objects:
            self._process_single(source)
        return self.results
