"""
Cache MongoDB minimal pour suivre les scrapes.
Configuration via variables d'environnement :
 - MONGO_URI (obligatoire pour activer)
 - MONGO_DB (défaut: cti)
 - MONGO_CACHE_COLLECTION (défaut: cache)
Le cache ne fait pas de suppression ni d'auto-save (Mongo gère la persistance).
"""
from __future__ import annotations

from typing import Optional, Dict, Any

try:
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover
    MongoClient = None

from tools.cache import CacheEntry


class MongoCache:
    def __init__(self, uri: str, db_name: str = "cti", collection: str = "cache"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self._client: Optional["MongoClient"] = None
        self._coll = None
        self._connect()

    def _connect(self):
        if MongoClient is None:
            return
        try:
            self._client = MongoClient(self.uri)
            self._coll = self._client[self.db_name][self.collection_name]
        except Exception:
            self._client = None
            self._coll = None

    def _collection(self):
        if self._coll is None:
            self._connect()
        return self._coll

    def get(self, url: str) -> Optional[CacheEntry]:
        coll = self._collection()
        if coll is None:
            return None
        doc = coll.find_one({"url": url})
        if not doc:
            return None
        return CacheEntry.from_dict(doc)

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
    ) -> CacheEntry:
        if extracted is None or keywords is None:
            existing = self.get(url)
            if existing:
                if extracted is None:
                    extracted = existing.extracted
                if keywords is None:
                    keywords = existing.keywords
        entry = CacheEntry(
            url=url,
            type=source_type,
            hash=hash_value,
            date=date,
            status=status,
            error=error,
            saved_path=saved_path,
            extracted=extracted,
            keywords=keywords,
        )
        coll = self._collection()
        if coll is not None:
            try:
                coll.update_one({"url": url}, {"$set": entry.to_dict()}, upsert=True)
            except Exception:
                pass
        return entry

    def has_changed(self, url: str, current_hash: Optional[str]) -> bool:
        cached = self.get(url)
        if cached is None:
            return True
        if cached.hash is None or current_hash is None:
            return True
        return cached.hash != current_hash

    def stats(self) -> Dict[str, Any]:
        coll = self._collection()
        if coll is None:
            return {"error": "mongo_unavailable", "db": self.db_name, "collection": self.collection_name}
        try:
            count = coll.count_documents({})
        except Exception as exc:
            return {"error": str(exc), "db": self.db_name, "collection": self.collection_name}
        return {"entries": count, "db": self.db_name, "collection": self.collection_name}

    def clear(self) -> Dict[str, Any]:
        coll = self._collection()
        if coll is None:
            return {"error": "mongo_unavailable", "db": self.db_name, "collection": self.collection_name}
        try:
            res = coll.delete_many({})
        except Exception as exc:
            return {"error": str(exc), "db": self.db_name, "collection": self.collection_name}
        return {"deleted": res.deleted_count, "db": self.db_name, "collection": self.collection_name}
