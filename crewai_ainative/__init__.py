"""
crewai-ainative — Configure crewai to use AINative's free LLMs + ZeroMemory.

No OpenAI key needed. Works with Llama 3.3 70B, Qwen3, DeepSeek 4, and Kimi K2.

Usage:
    from crewai_ainative import configure_crew
    from crewai import Agent, Task, Crew

    configure_crew()  # sets AINative as default LLM + memory backend

    agent = Agent(role="Researcher", goal="Research AI", backstory="Expert researcher")
    # Uses AINative Llama 3.3 70B — free, no OpenAI key needed

Refs #3952
"""

from crewai_ainative.config import (
    configure_crew,
    get_llm_config,
    get_memory_config,
    MODELS,
    DEFAULT_MODEL,
    API_BASE,
)
from crewai_ainative.provision import resolve_api_key

__all__ = [
    "configure_crew",
    "get_llm_config",
    "get_memory_config",
    "resolve_api_key",
    "MODELS",
    "DEFAULT_MODEL",
    "API_BASE",
]
__version__ = "0.1.0"
