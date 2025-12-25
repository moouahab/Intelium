from pathlib import Path
from typing import Any, Optional, Set

from tools.download_types import NetworkPolicy
from tools.config_utils import to_int, to_bool


def build_network_policy(network_conf: dict[str, Any]) -> NetworkPolicy:
    allow_domains = network_conf.get("allow_domains") or None
    if allow_domains:
        allow_domains = set(allow_domains)
    max_bytes = network_conf.get("max_bytes")
    max_bytes = to_int(max_bytes)
    connect_timeout = to_int(network_conf.get("connect_timeout"))
    read_timeout = to_int(network_conf.get("read_timeout"))
    return NetworkPolicy(
        enforce_https=to_bool(network_conf.get("enforce_https", True), default=True),
        block_private=to_bool(network_conf.get("block_private", True), default=True),
        allow_domains=allow_domains,
        max_bytes=max_bytes,
        timeout=to_int(network_conf.get("timeout", 10), default=10) or 10,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
    )


def build_crawler_settings(crawler_conf: dict[str, Any], fallback_allow_domains: Optional[Set[str]] = None) -> dict[str, Any]:
    max_depth = to_int(crawler_conf.get("max_depth", 2), default=2) or 2
    max_pages = to_int(crawler_conf.get("max_pages"))

    allow_domains: Set[str] = set(crawler_conf.get("allow_domains", []) or [])
    if not allow_domains and fallback_allow_domains:
        allow_domains = set(fallback_allow_domains)

    return {
        "max_depth": max_depth,
        "max_pages": max_pages,
        "same_domain_only": to_bool(crawler_conf.get("same_domain_only", True), default=True),
        "allow_domains": allow_domains,
        "respect_robots": to_bool(crawler_conf.get("respect_robots", True), default=True),
        "crawl_delay_seconds": to_int(crawler_conf.get("crawl_delay_seconds", 0), default=0) or 0,
        "max_concurrent": to_int(crawler_conf.get("max_concurrent", 1), default=1) or 1,
        "url_normalizer": crawler_conf.get("url_normalizer", "strip"),
        "user_agent": crawler_conf.get("user_agent"),
    }


def build_http_client_settings(crawler_conf: dict[str, Any]) -> dict[str, Any]:
    """
    Construit un bundle cohérent des paramètres HTTP issus du bloc crawler.
    Centralise respect_robots, délai entre requêtes et stratégie de retry.
    """
    return {
        "respect_robots": to_bool(crawler_conf.get("respect_robots", True), default=True),
        "crawl_delay_seconds": to_int(crawler_conf.get("crawl_delay_seconds", 0), default=0) or 0,
        "retry_attempts": to_int(crawler_conf.get("retry_attempts", 2), default=2) or 2,
        "retry_backoff_seconds": float(crawler_conf.get("retry_backoff_seconds", 0.5)),
        "user_agent": crawler_conf.get("user_agent"),
    }
