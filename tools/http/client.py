from typing import Optional, List, Dict
import time

from tools.download import download_source
from tools.download_types import DownloadResult, NetworkPolicy, StorageTarget
from tools.http.network import validate_url
from tools.http.policies import RobotsDelayPolicy
from tools.http.request_context import build_request_context
from tools.http.headless import fetch_headless


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

    def _next_user_agent(self) -> str | None:
        if self.user_agents:
            ua = self.user_agents[self._ua_idx % len(self.user_agents)]
            self._ua_idx += 1
            return ua
        return self.user_agent

    def _next_proxy(self) -> Optional[Dict[str, str]]:
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

    def fetch(self, source: dict, storage: Optional[StorageTarget] = None) -> DownloadResult:
        url = source.get("url")
        ctx = build_request_context(
            source,
            self.policy,
            self.auth_conf,
            self._robots_delay,
            default_user_agent=self._next_user_agent(),
            proxy=self._next_proxy(),
        )

        validation_error = validate_url(url, ctx.policy)
        if validation_error:
            return DownloadResult(status="error", content=None, error=validation_error)

        if not self._robots_delay.is_allowed(url, respect_override=ctx.respect_robots):
            return DownloadResult(status="blocked-robots", content=None, error="Robots.txt interdit l'accès")

        headless_requested = bool(source.get("overrides", {}).get("headless") or source.get("headless"))
        if headless_requested and source.get("type", "html") == "html":
            html = fetch_headless(
                url,
                timeout=ctx.policy.timeout,
                user_agent=ctx.headers.get("User-Agent"),
                proxy=(ctx.proxy.get("http") if isinstance(ctx.proxy, dict) else None),
            )
            if html:
                saved = None
                if storage:
                    saved = storage.path_for(".html")
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    saved.write_text(html)
                return DownloadResult(status="downloaded", content=html, content_type="text/html", saved_path=saved, status_code=200)

        attempt = 0
        while True:
            self._robots_delay.wait(url, delay_override=ctx.crawl_delay)
            result = download_source(source, policy=ctx.policy, storage=storage, headers=ctx.headers, proxies=ctx.proxy)
            if not self._should_retry(result, attempt):
                return result
            attempt += 1
            backoff = self._backoff_delay(result, attempt)
            time.sleep(backoff)
