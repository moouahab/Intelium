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
import time

import requests


def main():
    parser = argparse.ArgumentParser(description="Mistral LLM CLI (stdin -> stdout)")
    parser.add_argument("--model", default=os.environ.get("MISTRAL_MODEL", "mistral-large-latest"))
    parser.add_argument("--max-tokens", type=int, default=int(os.environ.get("MISTRAL_MAX_TOKENS", 1024)))
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("MISTRAL_TEMPERATURE", 0.2)))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("MISTRAL_TIMEOUT", 180)))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("MISTRAL_RETRIES", 2)))
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

    last_error = None
    for attempt in range(args.retries + 1):
        try:
            resp = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=args.timeout,
            )
        except Exception as exc:
            last_error = exc
            time.sleep(2 * (attempt + 1))
            continue

        if resp.status_code == 200:
            break
        last_error = f"HTTP {resp.status_code}: {resp.text}"
        time.sleep(2 * (attempt + 1))
    else:
        print(f"Erreur réseau vers Mistral: {last_error}", file=sys.stderr)
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
