import ipaddress
import socket
from urllib.parse import urlparse
import requests
from tools.providers.http.download_types import NetworkPolicy


def resolve_host_ips(host: str) -> list[str]:
    """
    Résout un hostname en adresses IP. Retourne une liste vide en cas d'échec pour ne pas bloquer inutilement.
    """
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return []
    ips = []
    for info in infos:
        try:
            addr = info[4][0]
        except Exception:
            continue
        ips.append(addr)
    return ips


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
    if policy.block_private and parsed.hostname:
        if is_private(parsed.hostname):
            return "Accès aux réseaux privés bloqué"
        resolved_ips = resolve_host_ips(parsed.hostname)
        if any(is_private(ip) for ip in resolved_ips):
            return "Résolution DNS vers réseau privé bloquée"
    if policy.allow_domains:
        host = parsed.hostname or ""
        if host not in policy.allow_domains:
            return "Domaine non autorisé"
    return None
