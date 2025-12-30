"""
Persistance optionnelle des résultats dans MongoDB.
Configuré via variables d'environnement :
- MONGO_URI (ex: mongodb://user:pass@host:27017)
- MONGO_DB (défaut: cti)
- MONGO_COLLECTION (défaut: results)

Si MONGO_URI n'est pas défini, rien n'est écrit.
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

try:
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover - pymongo peut ne pas être installé
    MongoClient = None

_client: Optional["MongoClient"] = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    uri = os.getenv("MONGO_URI")
    if not uri or MongoClient is None:
        return None
    db_name = os.getenv("MONGO_DB", "cti")
    coll_name = os.getenv("MONGO_COLLECTION", "results")
    try:
        _client = MongoClient(uri)
        _collection = _client[db_name][coll_name]
        return _collection
    except Exception:
        return None


def save_result(result: Dict[str, Any]) -> None:
    """
    Sauvegarde un document résultat dans MongoDB si configuré.
    """
    coll = _get_collection()
    if coll is None:
        return
    try:
        coll.insert_one(result)
    except Exception:
        # On ignore silencieusement pour ne pas casser le flux principal
        return
