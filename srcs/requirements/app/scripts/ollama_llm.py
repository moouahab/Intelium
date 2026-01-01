#!/usr/bin/env python3
"""
Client Ollama (stdin -> stdout).
Par défaut utilise l'API HTTP Ollama (OLLAMA_HOST), sinon fallback CLI si binaire dispo.
Exemple :
  echo "prompt" | python3 scripts/ollama_llm.py --model llama3.1:8b
Variables :
  OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_RETRIES, OLLAMA_HOST
  OLLAMA_NUM_CTX, OLLAMA_NUM_PREDICT, OLLAMA_TEMPERATURE
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from typing import Optional

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Ollama LLM CLI (stdin -> stdout)")
    parser.add_argument("--model", default=os.environ.get("OLLAMA_MODEL", "llama3.1:8b"))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("OLLAMA_TIMEOUT", 120)))
    parser.add_argument("--retries", type=int, default=int(os.environ.get("OLLAMA_RETRIES", 1)))
    parser.add_argument("--host", default=os.environ.get("OLLAMA_HOST", ""))
    args = parser.parse_args()

    prompt = sys.stdin.read()
    if not prompt.strip():
        print("Prompt vide sur stdin.", file=sys.stderr)
        return 1

    def _ollama_options():
        options = {}
        num_ctx = os.environ.get("OLLAMA_NUM_CTX")
        num_predict = os.environ.get("OLLAMA_NUM_PREDICT")
        temperature = os.environ.get("OLLAMA_TEMPERATURE")
        if num_ctx:
            try:
                options["num_ctx"] = int(num_ctx)
            except ValueError:
                pass
        if num_predict:
            try:
                options["num_predict"] = int(num_predict)
            except ValueError:
                pass
        if temperature:
            try:
                options["temperature"] = float(temperature)
            except ValueError:
                pass
        return options or None

    def _call_http(host: str) -> Optional[str]:
        url = host.rstrip("/") + "/api/generate"
        payload = {"model": args.model, "prompt": prompt, "stream": False}
        opts = _ollama_options()
        if opts:
            payload["options"] = opts
        resp = requests.post(
            url,
            json=payload,
            timeout=args.timeout,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        return data.get("response")

    def _call_cli() -> str:
        proc = subprocess.run(
            ["ollama", "run", args.model],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=args.timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or f"exit={proc.returncode}")
        return proc.stdout.strip()

    last_err = None
    for attempt in range(args.retries + 1):
        try:
            if args.host:
                result = _call_http(args.host)
            else:
                result = _call_cli()
            if result:
                sys.stdout.write(result.strip())
                return 0
            raise RuntimeError("Réponse Ollama vide")
        except Exception as exc:
            last_err = exc
            time.sleep(2 * (attempt + 1))

    print(f"Echec Ollama: {last_err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
