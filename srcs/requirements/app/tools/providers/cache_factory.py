from tools.interfaces import CacheBackend
from tools.providers.cache_store import build_cache_store


def build_cache(cache_conf: dict) -> CacheBackend:
    return build_cache_store(cache_conf)
