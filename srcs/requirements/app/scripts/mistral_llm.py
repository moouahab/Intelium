#!/usr/bin/env python3
"""
Client minimal pour appeler l'API Mistral en lisant le prompt sur stdin.
Clé attendue dans l'environnement MISTRAL_API_KEY.
Usage : echo "prompt" | python3 scripts/mistral_llm.py --model mistral-large-latest
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import requests


def main():
    parser = argparse.ArgumentParser(description="Mistral LLM CLI (stdin -> stdout)")
    parser.add_argument("--model", default=os.environ.get("MISTRAL_MODEL", "mistral-large-latest"))
    parser.add_argument("--max-tokens", type=int, default=int(os.environ.get("MISTRAL_MAX_TOKENS", 1024)))
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("MISTRAL_TEMPERATURE", 0.2)))
    args = parser.parse_args()

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("MISTRAL_API_KEY manquante.", file=sys.stderr)
        sys.exit(1)

    prompt = sys.stdin.read()
    if not prompt.strip():
        print("Prompt vide sur stdin.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
    }

    try:
        resp = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=60,
        )
    except Exception as exc:
        print(f"Erreur réseau vers Mistral: {exc}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code != 200:
        print(f"Echec Mistral ({resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        sys.exit(1)

    sys.stdout.write(content)


if __name__ == "__main__":
    main()
