from pathlib import Path
from tools.cache import CacheManager, CacheRegistry


def build_cache(cache_conf: dict) -> CacheManager | CacheRegistry:
    cache_file = cache_conf.get("file", "data/cache.json")
    auto_save = bool(cache_conf.get("auto_save", True))
    per_site = bool(cache_conf.get("per_site", False))
    if per_site:
        base_dir = cache_conf.get("dir", "data/cache_sites")
        return CacheRegistry(base_dir, auto_save=auto_save)
    return CacheManager(cache_file, auto_save=auto_save)
