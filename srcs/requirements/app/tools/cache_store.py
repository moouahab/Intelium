from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from tools.cache import CacheManager, CacheRegistry
from tools.cache_mongo import MongoCache
from tools.interfaces import CacheStore
from tools.secrets import get_secret


class FileCacheStore:
    def __init__(self, cache_file: str | Path, auto_save: bool = True):
        self._manager = CacheManager(cache_file, auto_save=auto_save)

    def get(self, url: str):
        return self._manager.get(url)

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: Optional[str] = None,
        date: Optional[str] = None,
        error: Optional[str] = None,
        saved_path: Optional[str] = None,
        extracted: Optional[list] = None,
        keywords: Optional[dict] = None,
    ):
        return self._manager.record_scrape(
            url=url,
            source_type=source_type,
            status=status,
            hash_value=hash_value,
            date=date,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        return self._manager.has_changed(url, current_hash)

    def stats(self) -> Dict[str, Any]:
        return self._manager.stats()

    def clear(self) -> Dict[str, Any]:
        return self._manager.clear()


class PerSiteCacheStore:
    def __init__(self, base_dir: str | Path, auto_save: bool = True):
        self._registry = CacheRegistry(base_dir, auto_save=auto_save)

    def get(self, url: str):
        return self._registry.get(url)

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: Optional[str] = None,
        date: Optional[str] = None,
        error: Optional[str] = None,
        saved_path: Optional[str] = None,
        extracted: Optional[list] = None,
        keywords: Optional[dict] = None,
    ):
        return self._registry.record_scrape(
            url=url,
            source_type=source_type,
            status=status,
            hash_value=hash_value,
            date=date,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        return self._registry.has_changed(url, current_hash)

    def stats(self) -> Dict[str, Any]:
        return self._registry.stats()

    def clear(self) -> Dict[str, Any]:
        return self._registry.clear()


class MongoCacheStore:
    def __init__(self, uri: str, db_name: str = "cti", collection: str = "cache"):
        self._mongo = MongoCache(uri=uri, db_name=db_name, collection=collection)

    def get(self, url: str):
        return self._mongo.get(url)

    def record_scrape(
        self,
        url: str,
        source_type: str,
        status: str,
        hash_value: Optional[str] = None,
        date: Optional[str] = None,
        error: Optional[str] = None,
        saved_path: Optional[str] = None,
        extracted: Optional[list] = None,
        keywords: Optional[dict] = None,
    ):
        return self._mongo.record_scrape(
            url=url,
            source_type=source_type,
            status=status,
            hash_value=hash_value,
            date=date,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        return self._mongo.has_changed(url, current_hash)

    def stats(self) -> Dict[str, Any]:
        return self._mongo.stats()

    def clear(self) -> Dict[str, Any]:
        return self._mongo.clear()


def build_cache_store(cache_conf: dict) -> CacheStore:
    backend = cache_conf.get("backend")
    mongo_uri = get_secret("MONGO_URI") or cache_conf.get("mongo_uri")
    if backend == "mongo" or mongo_uri:
        if mongo_uri:
            db_name = cache_conf.get("mongo_db", "cti")
            coll = cache_conf.get("mongo_collection", "cache")
            return MongoCacheStore(uri=mongo_uri, db_name=db_name, collection=coll)

    auto_save = bool(cache_conf.get("auto_save", True))
    per_site = bool(cache_conf.get("per_site", False))
    if per_site:
        base_dir = cache_conf.get("dir", "data/cache_sites")
        return PerSiteCacheStore(base_dir, auto_save=auto_save)
    cache_file = cache_conf.get("file", "data/cache.json")
    return FileCacheStore(cache_file, auto_save=auto_save)
