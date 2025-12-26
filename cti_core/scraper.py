from typing import Set
from concurrent.futures import ThreadPoolExecutor

from .Source import Source
from .crawler_state import CrawlerState
from cti_core.sources_factory import enqueue_links
from cti_core.result_recorder import ResultRecorder
from tools.cache import CacheManager
from tools.download_types import NetworkPolicy
from tools.http.url_utils import normalize_url, same_domain
import tools.parser as parser
from tools.keywords import find_keyword_hits
from tools.http.client import HttpClient
from tools.http.url_policy import UrlPolicy
from tools.parsers.text_utils import ensure_text


class Scraper:
    def __init__(self, config_model, cache_manager: CacheManager, http_client: HttpClient | None = None):
        self.config_model = config_model
        self.cache = cache_manager
        self.results = []
        self.policy: NetworkPolicy = config_model.network_policy
        crawler_conf = config_model.crawler_settings
        self.max_depth = crawler_conf.get("max_depth", 2)
        self.max_pages = crawler_conf.get("max_pages")
        self.same_domain_only = bool(crawler_conf.get("same_domain_only", True))
        self.allow_domains: Set[str] = set(crawler_conf.get("allow_domains", []) or [])
        self.max_concurrent = int(crawler_conf.get("max_concurrent", 1) or 1)
        http_settings = getattr(config_model, "http_settings", {}) or {}
        self.url_policy = UrlPolicy(
            same_domain_only=self.same_domain_only,
            allow_domains=self.allow_domains or None,
            normalizer_name=crawler_conf.get("url_normalizer", "strip"),
        )
        self.http_client = http_client or HttpClient(
            policy=self.policy,
            auth_conf=getattr(config_model, "auth_settings", {}),
            respect_robots=bool(http_settings.get("respect_robots", crawler_conf.get("respect_robots", True))),
            crawl_delay=int(http_settings.get("crawl_delay_seconds", crawler_conf.get("crawl_delay_seconds", 0))),
            retries=int(http_settings.get("retry_attempts", 2)),
            backoff_seconds=float(http_settings.get("retry_backoff_seconds", 0.5)),
            user_agent=http_settings.get("user_agent") or crawler_conf.get("user_agent"),
            user_agents=getattr(config_model, "user_agents", []),
            proxies=getattr(config_model, "proxies", []),
        )
        self.recorder = ResultRecorder(self.cache, self.results)

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

        result = self.http_client.fetch(
            source_dict,
            storage=storage,
        )
        current.status = result.status
        current.error = result.error
        current.content = result.content
        if result.status == "downloaded":
            current.update_hash()

        extracted = []
        keyword_hits = {}
        if result.status == "downloaded":
            extracted = parser.parse_content(
                current.type,
                current.content,
                self.config_model.scraping_settings,
                source_name=current.name,
            )
            texts_for_match = list(extracted)
            raw = result.content
            raw_text = ensure_text(raw) if raw is not None else ""
            if raw_text:
                texts_for_match.append(raw_text)
            keyword_hits = find_keyword_hits(texts_for_match, getattr(self.config_model, "keywords", {}))
        return result, extracted, keyword_hits

    def _process_source(self, state: CrawlerState, current: Source, depth: int) -> None:
        if state.already_visited(current.url):
            return
        state.mark_visited(current.url)

        if self.recorder.check_or_record_cache_hit(current.url, current.type, current.name or current.url):
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
            self._process_source(state, current, depth)

    def _process_single(self, source: Source):
        thread_safe = self.max_concurrent > 1
        state = CrawlerState(self.max_depth, self.max_pages, self._normalize_url, thread_safe=thread_safe)
        state.add(source, 0)

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
