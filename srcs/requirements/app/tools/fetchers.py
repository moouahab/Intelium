from __future__ import annotations

from typing import Optional

from tools.http.client import HttpClient
from tools.interfaces import GenericFetcher


class HttpFetcher:
    """
    Adaptateur simple autour de HttpClient pour exposer l'interface GenericFetcher.
    """

    def __init__(self, client: HttpClient):
        self.client = client

    def fetch(self, source: dict, storage=None):
        return self.client.fetch(source, storage=storage)


def build_fetcher(config_model, http_client: Optional[GenericFetcher] = None) -> GenericFetcher:
    if http_client is not None:
        return http_client
    http_settings = getattr(config_model, "http_settings", {}) or {}
    crawler_conf = config_model.crawler_settings
    client = HttpClient(
        policy=config_model.network_policy,
        auth_conf=getattr(config_model, "auth_settings", {}),
        respect_robots=bool(http_settings.get("respect_robots", crawler_conf.get("respect_robots", True))),
        crawl_delay=int(http_settings.get("crawl_delay_seconds", crawler_conf.get("crawl_delay_seconds", 0))),
        retries=int(http_settings.get("retry_attempts", 2)),
        backoff_seconds=float(http_settings.get("retry_backoff_seconds", 0.5)),
        user_agent=http_settings.get("user_agent") or crawler_conf.get("user_agent"),
        user_agents=getattr(config_model, "user_agents", []),
        proxies=getattr(config_model, "proxies", []),
    )
    return HttpFetcher(client)
