from typing import Optional, Set

from tools.providers.http.url_utils import resolve_normalizer, same_domain


class UrlPolicy:
    """
    Regroupe normalisation d'URL et filtrage de domaine (same_domain/allowlist).
    Partagé entre le scraper (enqueue) et d'autres composants si besoin.
    """

    def __init__(self, same_domain_only: bool = True, allow_domains: Optional[Set[str]] = None, normalizer_name: str = "strip"):
        self.same_domain_only = same_domain_only
        self.allow_domains = allow_domains
        self.normalizer = resolve_normalizer(normalizer_name)

    def normalize(self, url: str) -> str:
        return self.normalizer(url)

    def can_follow(self, base_url: str, target_url: str) -> bool:
        if not target_url:
            return False
        if not self.same_domain_only:
            if self.allow_domains:
                return same_domain(base_url, target_url, self.allow_domains)
            return True
        return same_domain(base_url, target_url, self.allow_domains)
