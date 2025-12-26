#!/usr/bin/env python3
"""
Client minimal pour appeler l'API Groq en lisant le prompt sur stdin.
La clé doit être fournie via l'env GROQ_API_KEY.
Usage : echo "prompt" | python3 scripts/groq_llm.py
"""
import os
import sys
import json
import argparse
import requests


def main():
    parser = argparse.ArgumentParser(description="Groq LLM CLI (stdin -> stdout)")
    parser.add_argument(
        "--model",
        default=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        help="Nom du modèle Groq (env GROQ_MODEL sinon). Ex: llama-3.3-70b-versatile, llama-3.1-8b-instant.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=int(os.environ.get("GROQ_MAX_TOKENS", 1024)),
        help="Limite de tokens de sortie.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("GROQ_TEMPERATURE", 0.2)),
        help="Température de génération.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY manquante dans l'environnement.", file=sys.stderr)
        sys.exit(1)

    prompt = sys.stdin.read()
    if not prompt.strip():
        print("Prompt vide sur stdin.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "model": args.model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "stream": False,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=60,
        )
    except Exception as exc:
        print(f"Erreur réseau vers Groq: {exc}", file=sys.stderr)
        sys.exit(1)

    if resp.status_code != 200:
        print(f"Echec Groq ({resp.status_code}): {resp.text}", file=sys.stderr)
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
