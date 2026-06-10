"""
crewai-ainative — Configuration

Sets environment variables and returns config dicts so crewai uses
AINative's OpenAI-compatible endpoint for all LLM calls.

CrewAI reads OPENAI_API_KEY, OPENAI_API_BASE, and OPENAI_MODEL_NAME
to configure its default LLM. We set these to AINative values.

Refs #3952
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Optional

from crewai_ainative.provision import resolve_api_key

API_BASE = "https://api.ainative.studio/api/v1"
MEMORY_API_BASE = "https://api.ainative.studio/api/v1/public/memory/v2"

# Model aliases -> full model identifiers
MODELS: Dict[str, str] = {
    # Meta Llama
    "llama": "meta-llama/Llama-3.3-70B-Instruct",
    "llama-70b": "meta-llama/Llama-3.3-70B-Instruct",
    "llama-8b": "meta-llama/Llama-3.1-8B-Instruct",
    # Qwen
    "qwen": "qwen3-coder-flash",
    "qwen-coder": "qwen3-coder-flash",
    # DeepSeek
    "deepseek": "deepseek-4-flash",
    "deepseek-flash": "deepseek-4-flash",
    # Kimi
    "kimi": "kimi-k2",
}

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct"


def get_model(alias: str) -> str:
    """
    Resolve a model alias to its full identifier.

    Args:
        alias: Short alias (e.g. "llama", "qwen") or full model ID.

    Returns:
        Full model identifier string.
    """
    return MODELS.get(alias, alias)


def get_llm_config(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> dict:
    """
    Return a dict of environment variable overrides for crewai's LLM.

    Args:
        model: Model alias or full ID. Defaults to Llama 3.3 70B.
        api_key: Explicit API key. Auto-provisions if not provided.
        api_base: Override API base URL.

    Returns:
        Dict with OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL_NAME.
    """
    key = resolve_api_key(api_key)
    base = api_base or API_BASE
    model_id = get_model(model) if model else DEFAULT_MODEL

    return {
        "OPENAI_API_KEY": key,
        "OPENAI_API_BASE": base,
        "OPENAI_MODEL_NAME": model_id,
    }


def get_memory_config(
    api_key: Optional[str] = None,
    entity: str = "crewai-agent",
) -> dict:
    """
    Return config for ZeroMemory integration with crewai.

    This provides the API endpoint and key for storing/recalling
    agent memories via ZeroDB's cognitive memory system.

    Args:
        api_key: Explicit API key. Uses resolved key if not provided.
        entity: Entity name for memory storage. Defaults to "crewai-agent".

    Returns:
        Dict with memory API configuration.
    """
    key = resolve_api_key(api_key)
    return {
        "memory_api_base": MEMORY_API_BASE,
        "api_key": key,
        "entity": entity,
    }


def configure_crew(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    verbose: bool = True,
) -> str:
    """
    Configure crewai to use AINative's free LLMs.

    Sets the environment variables that crewai reads for its default LLM:
    - OPENAI_API_KEY -> AINative API key
    - OPENAI_API_BASE -> AINative OpenAI-compatible endpoint
    - OPENAI_MODEL_NAME -> Selected model (default: Llama 3.3 70B)

    Also sets AINATIVE_API_KEY for ecosystem compatibility.

    Args:
        model: Model alias or full ID. Defaults to Llama 3.3 70B.
        api_key: Explicit API key. Auto-provisions if not provided.
        api_base: Override API base URL.
        verbose: Print configuration summary to stderr.

    Returns:
        The API key being used.

    Example:
        from crewai_ainative import configure_crew
        from crewai import Agent, Task, Crew

        configure_crew()

        agent = Agent(
            role="Researcher",
            goal="Research AI trends",
            backstory="Expert AI researcher",
        )
    """
    config = get_llm_config(model=model, api_key=api_key, api_base=api_base)

    # Set env vars for crewai
    os.environ["OPENAI_API_KEY"] = config["OPENAI_API_KEY"]
    os.environ["OPENAI_API_BASE"] = config["OPENAI_API_BASE"]
    os.environ["OPENAI_MODEL_NAME"] = config["OPENAI_MODEL_NAME"]

    # Also set AINATIVE_API_KEY for ecosystem tools
    os.environ["AINATIVE_API_KEY"] = config["OPENAI_API_KEY"]

    if verbose:
        key_preview = config["OPENAI_API_KEY"][:12] + "..."
        print(
            f"\n  crewai-ainative configured!\n"
            f"\n"
            f"  Model:    {config['OPENAI_MODEL_NAME']}\n"
            f"  API Base: {config['OPENAI_API_BASE']}\n"
            f"  API Key:  {key_preview}\n"
            f"\n"
            f"  All crewai agents will now use AINative's free LLMs.\n",
            file=sys.stderr,
        )

    return config["OPENAI_API_KEY"]
