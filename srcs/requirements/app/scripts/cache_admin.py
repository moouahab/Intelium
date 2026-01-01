#!/usr/bin/env python3
"""
Outil d'administration du cache (fichier, per-site ou Mongo).
Usage :
  python scripts/cache_admin.py --stats --file data/cache.json
  python scripts/cache_admin.py --clear --dir data/cache_sites
Options :
  --mongo-uri MONGO_URI   (fallback env/Vault via MONGO_URI)
  --db DB                 (defaut: cti)
  --collection COLLECTION (defaut: cache)
  --file PATH             (cache fichier, ex: data/cache.json)
  --dir PATH              (cache per-site, ex: data/cache_sites)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.cache_store import FileCacheStore, PerSiteCacheStore, MongoCacheStore
from tools.secrets import get_secret


def _run_action(store, args) -> dict:
    return store.stats() if args.stats else store.clear()


def main():
    parser = argparse.ArgumentParser(description="Admin cache (file, per-site ou Mongo)")
    parser.add_argument("--stats", action="store_true", help="Afficher les stats du cache")
    parser.add_argument("--clear", action="store_true", help="Purger le cache")
    parser.add_argument("--mongo-uri", help="URI Mongo (fallback env MONGO_URI)")
    parser.add_argument("--db", default="cti", help="Nom de la base Mongo (défaut: cti)")
    parser.add_argument("--collection", default="cache", help="Collection Mongo (défaut: cache)")
    parser.add_argument("--file", help="Chemin du cache fichier (ex: data/cache.json)")
    parser.add_argument("--dir", help="Chemin du cache per-site (ex: data/cache_sites)")
    args = parser.parse_args()

    if not args.stats and not args.clear:
        parser.error("Spécifie --stats ou --clear")

    file_path = Path(args.file) if args.file else None
    dir_path = Path(args.dir) if args.dir else None
    mongo_uri = args.mongo_uri or get_secret("MONGO_URI")

    results = {}
    if file_path:
        store = FileCacheStore(file_path, auto_save=False)
        results["file"] = _run_action(store, args)
    if dir_path:
        store = PerSiteCacheStore(dir_path, auto_save=False)
        results["dir"] = _run_action(store, args)
    if mongo_uri:
        store = MongoCacheStore(mongo_uri, db_name=args.db, collection=args.collection)
        results["mongo"] = _run_action(store, args)
    if not results:
        results["error"] = "Aucune cible : fournir --file, --dir ou --mongo-uri (ou MONGO_URI)"

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
