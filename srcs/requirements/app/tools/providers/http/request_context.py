from dataclasses import dataclass
from typing import Dict, Any, Optional

from tools.download_types import NetworkPolicy
from tools.auth import build_headers
from tools.providers.http.policies import policy_with_overrides, RobotsDelayPolicy
from tools.config.overrides import normalize_overrides, merge_headers
from tools.logger_utils import mask_sensitive_headers


@dataclass
class RequestContext:
    policy: NetworkPolicy
    headers: Dict[str, str]
    respect_robots: bool
    crawl_delay: int
    proxy: Optional[dict] = None


def build_request_context(
    source: dict,
    base_policy: NetworkPolicy,
    auth_conf: dict,
    robots_delay: RobotsDelayPolicy,
    default_user_agent: str | None = None,
    proxy: Optional[dict] = None,
) -> RequestContext:
    url = source.get("url")
    overrides = normalize_overrides(source.get("overrides", {}))
    policy = policy_with_overrides(base_policy, overrides)

    respect_robots = overrides.get("respect_robots", robots_delay.respect_robots)
    crawl_delay = overrides.get("crawl_delay_seconds", robots_delay.default_delay)
    try:
        crawl_delay_int = int(crawl_delay)
    except (TypeError, ValueError):
        crawl_delay_int = robots_delay.default_delay

    base_headers = build_headers(url, auth_conf)
    headers = merge_headers(
        base_headers=base_headers,
        override_headers=overrides.get("headers"),
        user_agent=overrides.get("user_agent") or default_user_agent,
    )
    # On peut logger les headers masqués si besoin côté appelant
    masked_headers = mask_sensitive_headers(headers)
    return RequestContext(
        policy=policy,
        headers=headers,
        respect_robots=bool(respect_robots),
        crawl_delay=crawl_delay_int,
        proxy=proxy,
    )
