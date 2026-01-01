from __future__ import annotations

import os
from typing import Optional, Dict, Any

from tools.secrets import get_secret
from tools.interfaces import ResultStore

try:
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover - pymongo peut ne pas être installé
    MongoClient = None


class NoopResultStore:
    def save(self, result: Dict[str, Any]) -> None:
        return None


class MongoResultStore:
    def __init__(self, uri: str, db_name: str = "cti", collection: str = "results"):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self._client: Optional["MongoClient"] = None
        self._coll = None
        self._connect()

    def _connect(self) -> None:
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

    def save(self, result: Dict[str, Any]) -> None:
        coll = self._collection()
        if coll is None:
            return
        try:
            coll.insert_one(dict(result))
        except Exception:
            return


def build_result_store() -> ResultStore:
    uri = get_secret("MONGO_URI")
    if not uri:
        return NoopResultStore()
    db_name = os.getenv("MONGO_DB", "cti")
    collection = os.getenv("MONGO_COLLECTION", "results")
    return MongoResultStore(uri=uri, db_name=db_name, collection=collection)
