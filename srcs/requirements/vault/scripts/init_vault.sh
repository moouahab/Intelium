#!/usr/bin/env bash
set -euo pipefail

# Initialise et unseal Vault dans le conteneur cti-vault, puis affiche les clés.
# Usage : ./srcs/requirements/vault/scripts/init_vault.sh

COMPOSE="docker compose -f srcs/docker-compose.yml"
VAULT_CONTAINER="cti-vault"
VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
RETRIES=${RETRIES:-20}
SLEEP_SECONDS=${SLEEP_SECONDS:-1}

echo "[vault] Démarrage du service vault si nécessaire..."
$COMPOSE up -d vault >/dev/null

echo "[vault] Vérification de l'état (attente du démarrage du service)..."
STATUS_JSON=""
for i in $(seq 1 "$RETRIES"); do
  STATUS_JSON=$(docker exec "$VAULT_CONTAINER" sh -c "VAULT_ADDR='$VAULT_ADDR' vault status -format=json" 2>/dev/null || true)
  if echo "$STATUS_JSON" | grep -q '"initialized"'; then
    break
  fi
  echo "[vault] Vault pas prêt (tentative $i/$RETRIES), nouvelle tentative dans $SLEEP_SECONDS s..."
  sleep "$SLEEP_SECONDS"
done

if ! echo "$STATUS_JSON" | grep -q '"initialized"'; then
  echo "[vault] Échec : Vault ne répond pas après $RETRIES tentatives."
  exit 1
fi

if echo "$STATUS_JSON" | grep -q '"initialized":true'; then
  echo "[vault] Déjà initialisé."
  # Si Vault est scellé, on ne peut pas récupérer l'unseal key automatiquement : l'utilisateur doit l'avoir conservée.
  SEALED=$(echo "$STATUS_JSON" | python - <<'PY'
import json, sys
data = json.load(sys.stdin)
print(data.get("sealed", True))
PY
  )
  if [ "$SEALED" = "True" ]; then
    if [ -n "${UNSEAL_KEY:-}" ]; then
      echo "[vault] Tentative d'unseal avec UNSEAL_KEY de l'environnement..."
      docker exec "$VAULT_CONTAINER" sh -c "VAULT_ADDR='$VAULT_ADDR' vault operator unseal $UNSEAL_KEY" >/dev/null
      echo "[vault] Unseal tenté. Vérifie le status ci-dessous."
      docker exec "$VAULT_CONTAINER" sh -c "VAULT_ADDR='$VAULT_ADDR' vault status"
    else
      echo "[vault] Vault est scellé. Fournis UNSEAL_KEY=<clé> dans l'env ou lance vault operator unseal manuellement."
    fi
  else
    echo "[vault] Vault est déjà unseal."
  fi
  exit 0
fi

echo "[vault] Initialisation (1 clé, seuil 1)..."
INIT_OUT=$(docker exec "$VAULT_CONTAINER" sh -c "VAULT_ADDR='$VAULT_ADDR' vault operator init -key-shares=1 -key-threshold=1 -format=json")

ROOT_TOKEN=$(python - <<'PY'
import json, os
data = json.loads(os.environ["INIT_OUT"])
print(data["root_token"])
PY
)

UNSEAL_KEY=$(python - <<'PY'
import json, os
data = json.loads(os.environ["INIT_OUT"])
print(data["unseal_keys_b64"][0])
PY
)

echo "[vault] Unseal..."
docker exec "$VAULT_CONTAINER" sh -c "VAULT_ADDR='$VAULT_ADDR' vault operator unseal $UNSEAL_KEY" >/dev/null

cat <<EOF
[vault] Initialisation terminée.
VAULT_ADDR=$VAULT_ADDR
VAULT_TOKEN=$ROOT_TOKEN
UNSEAL_KEY=$UNSEAL_KEY

> Ajoute VAULT_TOKEN (et éventuellement VAULT_ADDR) dans ton .env pour que le scraper puisse lire les secrets.
> Conserve l'UNSEAL_KEY hors Git et hors .env (à stocker en lieu sûr).
EOF
