#!/usr/bin/env python3
"""
Outil d'administration du cache (fichier ou Mongo).
Usage :
  python scripts/cache_admin.py --stats
  python scripts/cache_admin.py --clear
Options :
  --mongo-uri MONGO_URI   (sinon lit MONGO_URI de l'env)
  --db DB                 (défaut: cti)
  --collection COLLECTION (défaut: cache)
  --file PATH             (cache fichier, ex: data/cache.json)
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Optional


def _load_file_cache(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text() or "{}")
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _stats_file(path: Path) -> dict:
    data = _load_file_cache(path)
    return {"entries": len(data), "path": str(path)}


def _clear_file(path: Path) -> dict:
    if path.exists():
        path.unlink()
    return {"cleared": True, "path": str(path)}


def _get_mongo_client(uri: str):
    try:
        from pymongo import MongoClient  # type: ignore
    except Exception as exc:  # pragma: no cover
        print(f"pymongo non disponible: {exc}")
        return None
    try:
        return MongoClient(uri, serverSelectionTimeoutMS=5000)
    except Exception as exc:
        print(f"Connexion Mongo échouée: {exc}")
        return None


def _stats_mongo(uri: str, db: str, coll: str) -> dict:
    client = _get_mongo_client(uri)
    if client is None:
        return {"error": "mongo_client_unavailable"}
    try:
        count = client[db][coll].count_documents({})
        return {"uri": uri, "db": db, "collection": coll, "entries": count}
    except Exception as exc:
        return {"error": str(exc)}


def _clear_mongo(uri: str, db: str, coll: str) -> dict:
    client = _get_mongo_client(uri)
    if client is None:
        return {"error": "mongo_client_unavailable"}
    try:
        res = client[db][coll].delete_many({})
        return {"uri": uri, "db": db, "collection": coll, "deleted": res.deleted_count}
    except Exception as exc:
        return {"error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Admin cache (file ou Mongo)")
    parser.add_argument("--stats", action="store_true", help="Afficher les stats du cache")
    parser.add_argument("--clear", action="store_true", help="Purger le cache")
    parser.add_argument("--mongo-uri", help="URI Mongo (fallback env MONGO_URI)")
    parser.add_argument("--db", default="cti", help="Nom de la base Mongo (défaut: cti)")
    parser.add_argument("--collection", default="cache", help="Collection Mongo (défaut: cache)")
    parser.add_argument("--file", help="Chemin du cache fichier (ex: data/cache.json)")
    args = parser.parse_args()

    if not args.stats and not args.clear:
        parser.error("Spécifie --stats ou --clear")

    file_path = Path(args.file) if args.file else None
    mongo_uri = args.mongo_uri or os.getenv("MONGO_URI")

    results = {}
    if file_path:
        results["file"] = _stats_file(file_path) if args.stats else _clear_file(file_path)
    if mongo_uri:
        results["mongo"] = _stats_mongo(mongo_uri, args.db, args.collection) if args.stats else _clear_mongo(mongo_uri, args.db, args.collection)
    if not file_path and not mongo_uri:
        results["error"] = "Aucune cible : fournisse --file ou --mongo-uri (ou MONGO_URI)"

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
