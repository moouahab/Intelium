"""
Récupération de secrets via variables d'environnement ou Vault (optionnel).
- Si la variable d'env <KEY> est présente, on l'utilise.
- Sinon, si VAULT_ADDR et VAULT_TOKEN sont définis et hvac installé, on tente de lire
  un secret KV v2 à l'emplacement VAULT_SECRET_PATH (défaut: secret/data/cti).
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import hvac  # type: ignore
except Exception:  # pragma: no cover
    hvac = None


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    # Priorité env
    val = os.getenv(key)
    if val:
        return val
    # Vault (optionnel)
    if hvac is None:
        return default
    addr = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")
    path = os.getenv("VAULT_SECRET_PATH", "secret/data/cti")
    if not addr or not token:
        return default
    try:
        client = hvac.Client(url=addr, token=token)
        resp = client.secrets.kv.v2.read_secret_version(path=path)
        data = resp.get("data", {}).get("data", {})
        return data.get(key, default)
    except Exception:
        return default
