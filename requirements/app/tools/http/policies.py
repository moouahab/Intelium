import time
import threading
import urllib.robotparser
from urllib.parse import urlparse
from tools.download_types import NetworkPolicy
from tools.config_utils import to_int


class RobotsDelayPolicy:
    """
    Encapsule le respect de robots.txt et le délai entre requêtes par hôte.
    Thread-safe grâce à un verrou interne.
    """

    def __init__(self, respect_robots: bool = True, default_delay: int = 0):
        self.respect_robots = respect_robots
        self.default_delay = default_delay
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_access: dict[str, float] = {}
        self._lock = threading.Lock()

    def is_allowed(self, url: str, respect_override: bool | None = None) -> bool:
        respect = self.respect_robots if respect_override is None else respect_override
        if not respect:
            return True
        host = urlparse(url).netloc
        with self._lock:
            parser = self._robots_cache.get(host)
            if not parser:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"https://{host}/robots.txt")
                try:
                    rp.read()
                except Exception:
                    rp = None
                parser = rp
                self._robots_cache[host] = parser
        if parser is None:
            return True
        return parser.can_fetch("*", url)

    def wait(self, url: str, delay_override: int | None = None) -> None:
        delay = self.default_delay if delay_override is None else delay_override
        if delay <= 0:
            return
        host = urlparse(url).netloc
        now = time.time()
        with self._lock:
            last = self._last_access.get(host)
        wait = 0
        if last:
            wait = delay - (now - last)
        if wait > 0:
            time.sleep(wait)
        with self._lock:
            self._last_access[host] = time.time()


def policy_with_overrides(base_policy: NetworkPolicy, overrides: dict | None) -> NetworkPolicy:
    if not overrides:
        return base_policy
    max_bytes = overrides.get("max_bytes")
    max_bytes_int = to_int(max_bytes) if max_bytes is not None else base_policy.max_bytes
    timeout = overrides.get("request_timeout_seconds", base_policy.timeout)
    timeout_int = to_int(timeout, default=base_policy.timeout) or base_policy.timeout
    # Conserve l'ensemble des garde-fous (TLS, sandbox, scan) et ne modifie que les champs overridables
    return NetworkPolicy(
        enforce_https=base_policy.enforce_https,
        block_private=base_policy.block_private,
        allow_domains=base_policy.allow_domains,
        max_bytes=max_bytes_int,
        timeout=timeout_int,
        connect_timeout=base_policy.connect_timeout,
        read_timeout=base_policy.read_timeout,
        verify_ssl=base_policy.verify_ssl,
        ca_bundle=base_policy.ca_bundle,
        pinned_fingerprints=base_policy.pinned_fingerprints,
        scanner=base_policy.scanner,
        scan_command=base_policy.scan_command,
        scan_timeout=base_policy.scan_timeout,
        sanitize_downloads=base_policy.sanitize_downloads,
        sandbox_dir=base_policy.sandbox_dir,
    )
