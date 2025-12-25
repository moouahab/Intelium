"""
Utilitaires d'exécution LLM en CLI avec gestion sécurisée du prompt.
- Permet de passer le prompt via stdin ou via un fichier temporaire pour éviter
  les erreurs "argument list too long" ou les CLIs qui ne lisent pas stdin.
"""
from __future__ import annotations

import shlex
import subprocess
import tempfile
from typing import Optional


def run_cli_llm(
    command: str,
    prompt: str,
    timeout: int = 120,
    pass_prompt_as_arg: bool = False,
    prompt_via_file: bool = False,
) -> str:
    """
    Exécute une commande LLM locale.
    - pass_prompt_as_arg : ajoute le prompt (ou le chemin du fichier) aux arguments
    - prompt_via_file : écrit le prompt dans un fichier temporaire pour éviter les lignes trop longues
      et le passe en stdin (ou en argument si pass_prompt_as_arg=True)
    """
    cmd_list = shlex.split(command)
    run_kwargs = {"text": True, "capture_output": True, "timeout": timeout}

    if prompt_via_file:
        with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp:
            tmp.write(prompt)
            tmp.flush()
            if pass_prompt_as_arg:
                cmd_list = cmd_list + [tmp.name]
                run_kwargs["input"] = None
            else:
                tmp.seek(0)
                run_kwargs["stdin"] = tmp
                run_kwargs["input"] = None
                # subprocess.run lit stdin si fourni
            proc = subprocess.run(cmd_list, **run_kwargs)
    else:
        if pass_prompt_as_arg:
            cmd_list = cmd_list + [prompt]
            run_kwargs["input"] = None
        else:
            run_kwargs["input"] = prompt
        proc = subprocess.run(cmd_list, **run_kwargs)

    if proc.returncode != 0:
        raise RuntimeError(f"Commande IA échouée ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout.strip()
