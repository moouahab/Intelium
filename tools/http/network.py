import ipaddress
from urllib.parse import urlparse
import requests
from tools.download_types import NetworkPolicy


def is_private(host: str) -> bool:
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private
    except ValueError:
        return False


def validate_url(url: str, policy: NetworkPolicy) -> str | None:
    parsed = urlparse(url)
    if policy.enforce_https and parsed.scheme == "http":
        return "HTTPS requis"
    if policy.block_private and parsed.hostname and is_private(parsed.hostname):
        return "Accès aux réseaux privés bloqué"
    if policy.allow_domains:
        host = parsed.hostname or ""
        if host not in policy.allow_domains:
            return "Domaine non autorisé"
    return None
