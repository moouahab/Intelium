import ipaddress
import socket
import hashlib
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests
from tools.providers.http.download_types import NetworkPolicy


def resolve_host_ips(host: str) -> list[str]:
    """
    Résout un hostname en adresses IP. Une liste vide est refusée par validate_url.
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
        return not ip.is_global or ip.is_multicast
    except ValueError:
        return False


def validate_url(url: str, policy: NetworkPolicy) -> str | None:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return "URL HTTP(S) avec hôte requise"
        parsed.port  # valide aussi le port avant le transport
        if parsed.username is not None or parsed.password is not None:
            return "Identifiants dans l'URL interdits"
    except (ValueError, TypeError, AttributeError):
        return "URL invalide"
    if policy.enforce_https and parsed.scheme != "https":
        return "HTTPS requis"
    if policy.allow_domains and parsed.hostname not in policy.allow_domains:
        return "Domaine non autorisé"
    if policy.block_private and parsed.hostname:
        if is_private(parsed.hostname):
            return "Accès aux réseaux privés bloqué"
        resolved_ips = resolve_host_ips(parsed.hostname)
        if not resolved_ips:
            return "Résolution DNS impossible"
        if any(is_private(ip) for ip in resolved_ips):
            return "Résolution DNS vers réseau privé bloquée"
    return None


SAFE_REDIRECT_HEADERS = {"user-agent", "accept", "accept-language", "accept-encoding"}


def _origin(url):
    parsed = urlparse(url)
    return parsed.scheme, parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)


def get_response(url, policy, headers=None, proxies=None, redirect_headers=None):
    """GET borné : contrôle chaque saut avant connexion, sans redirection automatique.

    Les en-têtes applicatifs restent liés à leur origine. Une nouvelle origine
    ne reçoit que les en-têtes neutres et ses propres identifiants explicites.
    """
    if policy.offline:
        raise ValueError("Mode offline actif")
    current_headers = dict(headers or {})
    timeout = (
        (policy.connect_timeout or policy.timeout, policy.read_timeout or policy.timeout)
        if policy.connect_timeout or policy.read_timeout else policy.timeout
    )
    for hop in range(11):
        error = validate_url(url, policy)
        if error:
            raise ValueError(error)
        response = requests.get(
            url, timeout=timeout, stream=True, headers=current_headers,
            proxies=proxies, verify=policy.ca_bundle or policy.verify_ssl,
            allow_redirects=False,
        )
        try:
            if policy.pinned_fingerprints:
                cert = response.raw.connection.sock.getpeercert(binary_form=True)
                if hashlib.sha256(cert).hexdigest() not in policy.pinned_fingerprints:
                    raise ValueError("Certificat TLS non autorisé (pinning)")
            if response.status_code not in {301, 302, 303, 307, 308}:
                return response
            location = response.headers.get("Location")
            if not location:
                raise ValueError("Redirection sans destination")
            if hop == 10:
                raise ValueError("Trop de redirections HTTP")
            target = urljoin(url, location)
            error = validate_url(target, policy)
            if error:
                raise ValueError(error)
            if _origin(url) != _origin(target):
                current_headers = {k: v for k, v in current_headers.items() if k.lower() in SAFE_REDIRECT_HEADERS}
                if redirect_headers:
                    current_headers.update(redirect_headers(target))
            url = target
        except Exception:
            response.close()
            raise
        response.close()
