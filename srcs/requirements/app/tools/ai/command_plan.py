from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import shutil


@dataclass
class AiCommandPlan:
    mode: str
    command: Optional[str]
    langgraph_command: Optional[str]
    timeout: int
    pass_prompt_as_arg: bool
    prompt_via_file: bool


def detect_local_llm() -> Optional[str]:
    """
    Essaie de détecter un binaire LLM local et retourne une commande prête à l'emploi.
    Priorité : ollama -> llama/llama.cpp -> codex -> copilot -> code.
    """
    if shutil.which("ollama"):
        return "ollama run llama3.1:8b"
    if shutil.which("llama"):
        return "llama -m model.gguf"
    if shutil.which("llama.cpp"):
        return "llama.cpp -m model.gguf"
    if shutil.which("codex"):
        return "codex chat"
    if shutil.which("copilot"):
        return "copilot chat"
    if shutil.which("code"):
        return "code"
    return None


def build_command_plan(ai_conf: dict, logger=None) -> AiCommandPlan:
    mode = ai_conf.get("mode", "cli")
    prompt_via_file = bool(ai_conf.get("prompt_via_file", False))
    pass_prompt_as_arg_opt = ai_conf.get("pass_prompt_as_arg")
    command = ai_conf.get("command")
    langgraph_command = ai_conf.get("langgraph_llm_command")

    if pass_prompt_as_arg_opt is None:
        if command and any(token in command for token in ["codex", "copilot", "code"]):
            pass_prompt_as_arg = False if prompt_via_file else True
        else:
            pass_prompt_as_arg = False
    else:
        pass_prompt_as_arg = bool(pass_prompt_as_arg_opt)

    if not command:
        command = detect_local_llm()
        if not command and logger:
            logger.warning("AI report demandé mais aucune commande fournie ou détectée.")

    timeout = int(ai_conf.get("timeout", 120))
    return AiCommandPlan(
        mode=mode,
        command=command,
        langgraph_command=langgraph_command,
        timeout=timeout,
        pass_prompt_as_arg=pass_prompt_as_arg,
        prompt_via_file=prompt_via_file,
    )
