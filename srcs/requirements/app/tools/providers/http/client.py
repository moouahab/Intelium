from typing import Optional, List, Dict
import time
import threading
from contextlib import contextmanager

from tools.download import download_with_context
from tools.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.providers.http.network import validate_url
from tools.providers.http.policies import RobotsDelayPolicy
from tools.providers.http.request_context import build_request_context
from tools.logger_utils import mask_sensitive_headers
from tools.providers.http.headless import fetch_headless, HeadlessStrategy, get_default_headless_strategy
from tools.observability.metrics import record_fetch
from urllib.parse import urlparse, urlunparse


class HttpClient:
    """
    Client HTTP qui applique :
    - validation URL (HTTPS/allowlist/block_private)
    - respect robots.txt (optionnel)
    - délai entre requêtes par host
    - injection d'entêtes d'auth
    """

    def __init__(
        self,
        policy: NetworkPolicy,
        auth_conf: Optional[dict] = None,
        respect_robots: bool = True,
        crawl_delay: int = 0,
        retries: int = 2,
        backoff_seconds: float = 0.5,
        user_agent: str | None = None,
        user_agents: Optional[List[str]] = None,
        proxies: Optional[List[str]] = None,
        headless_strategy: Optional[HeadlessStrategy] = None,
        logger=None,
    ):
        self.policy = policy
        self.auth_conf = auth_conf or {}
        self._robots_delay = RobotsDelayPolicy(respect_robots=respect_robots, default_delay=crawl_delay)
        self.retries = max(0, int(retries))
        self.backoff_seconds = float(backoff_seconds)
        self.user_agent = user_agent
        self.user_agents = user_agents or []
        self._ua_idx = 0
        self.proxies = proxies or []
        self._proxy_idx = 0
        self.retryable_statuses = {403, 429, 500, 502, 503, 504}
        self.logger = logger
        self._lock = threading.Lock()
        self.metrics_path = getattr(policy, "metrics_path", None)  # optionnel, injecté via policy si présent
        self.headless_strategy = headless_strategy or get_default_headless_strategy()

    @contextmanager
    def _timed_fetch(self):
        start = time.time()
        yield lambda: time.time() - start

    def _next_user_agent(self) -> str | None:
        with self._lock:
            if self.user_agents:
                ua = self.user_agents[self._ua_idx % len(self.user_agents)]
                self._ua_idx += 1
                return ua
            return self.user_agent

    def _next_proxy(self) -> Optional[Dict[str, str]]:
        with self._lock:
            if not self.proxies:
                return None
            proxy = self.proxies[self._proxy_idx % len(self.proxies)]
            self._proxy_idx += 1
            # requests accepte un dict {"http": "...", "https": "..."}
            return {"http": proxy, "https": proxy}

    def _should_retry(self, result: DownloadResult, attempt: int) -> bool:
        if attempt >= self.retries:
            return False
        if result.status in {"error", "http-error"} and result.status_code in self.retryable_statuses:
            return True
        return False

    def _backoff_delay(self, result: DownloadResult, attempt: int) -> float:
        """
        Backoff adaptatif : + agressif sur 429/403.
        attempt est l'indice de tentative déjà effectuée (>=0).
        """
        factor = 1.0
        if result.status_code == 429:
            factor = 3.0
        elif result.status_code == 403:
            factor = 2.0
        return self.backoff_seconds * (attempt + 1) * factor

    def _run_headless(self, url: str, ctx, storage: Optional[StorageTarget]) -> DownloadResult | None:
        if not self.headless_strategy:
            return None
        html = self.headless_strategy.fetch(
            url,
            timeout=ctx.policy.timeout,
            user_agent=ctx.headers.get("User-Agent"),
            proxy=(ctx.proxy.get("http") if isinstance(ctx.proxy, dict) else None),
        )
        if not html:
            return None
        saved = None
        if storage:
            saved = storage.path_for(".html")
            saved.parent.mkdir(parents=True, exist_ok=True)
            saved.write_text(html)
        return DownloadResult(status="downloaded", content=html, content_type="text/html", saved_path=saved, status_code=200)

    def _fetch_with_retries(self, url: str, source: dict, ctx, storage: Optional[StorageTarget]) -> DownloadResult:
        attempt = 0
        with self._timed_fetch() as elapsed:
            while True:
                self._robots_delay.wait(url, delay_override=ctx.crawl_delay)
                result = download_with_context(source, ctx=ctx, storage=storage)
                if self.metrics_path:
                    safe_url = None
                    try:
                        parsed = urlparse(url or "")
                        safe_url = urlunparse(parsed._replace(query="", fragment=""))
                    except Exception:
                        safe_url = url
                    reason = None
                    if result.status == "blocked-robots":
                        reason = "blocked-robots"
                    elif result.status == "http-error" and result.status_code:
                        reason = f"http-{result.status_code}"
                    elif result.status == "offline":
                        reason = "offline"
                    elif result.error:
                        reason = (result.error[:80] if isinstance(result.error, str) else str(result.error)) or result.status
                    else:
                        reason = result.status
                    record_fetch(
                        self.metrics_path,
                        elapsed(),
                        result.status,
                        reason=reason,
                        size_bytes=result.size_bytes,
                        source_name=source.get("name"),
                        url=safe_url,
                    )
                    if self.logger and result.status != "downloaded":
                        try:
                            self.logger.warning("HTTP fetch KO %s status=%s reason=%s", safe_url, result.status, reason)
                        except Exception:
                            pass
                if not self._should_retry(result, attempt):
                    return result
                attempt += 1
                backoff = self._backoff_delay(result, attempt)
                time.sleep(backoff)

    def fetch(self, source: dict, storage: Optional[StorageTarget] = None) -> DownloadResult:
        url = source.get("url")
        if getattr(self.policy, "offline", False):
            return DownloadResult(status="offline", content=None, error="Mode offline actif (cache uniquement)")
        ctx = build_request_context(
            source,
            self.policy,
            self.auth_conf,
            self._robots_delay,
            default_user_agent=self._next_user_agent(),
            proxy=self._next_proxy(),
        )

        if self.logger:
            try:
                self.logger.debug(
                    "HTTP fetch %s proxy=%s headers=%s",
                    url,
                    ctx.proxy,
                    mask_sensitive_headers(ctx.headers),
                )
            except Exception:
                pass

        validation_error = validate_url(url, ctx.policy)
        if validation_error:
            return DownloadResult(status="error", content=None, error=validation_error)

        if not self._robots_delay.is_allowed(url, respect_override=ctx.respect_robots):
            return DownloadResult(status="blocked-robots", content=None, error="Robots.txt interdit l'accès")

        headless_requested = bool(source.get("overrides", {}).get("headless") or source.get("headless"))
        if headless_requested and source.get("type", "html") == "html":
            headless_result = self._run_headless(url, ctx, storage)
            if headless_result:
                return headless_result

        return self._fetch_with_retries(url, source, ctx, storage)
