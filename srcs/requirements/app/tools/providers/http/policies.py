import time
import threading
import urllib.robotparser
from dataclasses import replace
from tools.providers.http.network import get_response
from urllib.parse import urlparse
from tools.providers.http.download_types import NetworkPolicy
from tools.config.config_utils import to_int


class RobotsDelayPolicy:
    """
    Encapsule le respect de robots.txt et le délai entre requêtes par hôte.
    Thread-safe grâce à un verrou interne.
    """

    def __init__(self, respect_robots: bool = True, default_delay: int = 0, network_policy: NetworkPolicy | None = None):
        self.network_policy = network_policy or NetworkPolicy()
        self.respect_robots = respect_robots
        self.default_delay = default_delay
        self._robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._last_access: dict[str, float] = {}
        self._lock = threading.Lock()

    def is_allowed(self, url: str, respect_override: bool | None = None) -> bool:
        respect = self.respect_robots if respect_override is None else respect_override
        if not respect:
            return True
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        with self._lock:
            parser = self._robots_cache.get(host)
            if not parser:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{host}/robots.txt")
                try:
                    response = get_response(rp.url, self.network_policy)
                    try:
                        if response.status_code in {401, 403}:
                            rp.disallow_all = True
                        elif response.status_code >= 400:
                            rp.allow_all = True
                        else:
                            body = bytearray()
                            for chunk in response.iter_content(chunk_size=8192):
                                body.extend(chunk)
                                if len(body) > 262144:
                                    raise ValueError("robots.txt trop volumineux")
                            rp.parse(body.decode("utf-8", errors="replace").splitlines())
                    finally:
                        response.close()
                except Exception:
                    rp.disallow_all = True
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
    return replace(base_policy, max_bytes=max_bytes_int, timeout=timeout_int)
