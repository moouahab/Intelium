from urllib.parse import urlparse, urljoin


def normalize_url(url: str) -> str:
    return url.strip()


def normalize_url_lower(url: str) -> str:
    return url.strip().lower()


def resolve_normalizer(name: str | None):
    mapping = {
        None: normalize_url,
        "strip": normalize_url,
        "lower": normalize_url_lower,
        "strip-lower": normalize_url_lower,
    }
    if name in mapping:
        return mapping[name]
    raise ValueError(f"Normaliseur d'URL inconnu: {name}")


def same_domain(base: str, target: str, allow_domains=None) -> bool:
    try:
        base_host = urlparse(base).hostname or ""
        target_host = urlparse(target).hostname or ""
    except Exception:
        return False
    if allow_domains:
        return target_host in allow_domains
    return base_host == target_host


def join_url(base: str, link: str) -> str:
    return urljoin(base, link)
