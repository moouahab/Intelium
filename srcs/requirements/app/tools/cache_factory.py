from pathlib import Path
import os
from tools.cache import CacheManager, CacheRegistry
from tools.cache_mongo import MongoCache
from tools.secrets import get_secret


def build_cache(cache_conf: dict) -> CacheManager | CacheRegistry | MongoCache:
    backend = cache_conf.get("backend")
    mongo_uri = get_secret("MONGO_URI") or cache_conf.get("mongo_uri")
    if backend == "mongo" or mongo_uri:
        uri = mongo_uri
        db_name = cache_conf.get("mongo_db", "cti")
        coll = cache_conf.get("mongo_collection", "cache")
        if uri:
            return MongoCache(uri=uri, db_name=db_name, collection=coll)

    cache_file = cache_conf.get("file", "data/cache.json")
    auto_save = bool(cache_conf.get("auto_save", True))
    per_site = bool(cache_conf.get("per_site", False))
    if per_site:
        base_dir = cache_conf.get("dir", "data/cache_sites")
        return CacheRegistry(base_dir, auto_save=auto_save)
    return CacheManager(cache_file, auto_save=auto_save)
