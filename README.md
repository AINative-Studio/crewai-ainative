# crewai-ainative

Configure [crewai](https://github.com/crewAIInc/crewAI) to use AINative's free LLMs + ZeroMemory. No OpenAI key needed.

**Zero setup.** Works with Llama 3.3 70B, Qwen3, DeepSeek 4, and Kimi K2 — all free.

## Install

```bash
pip install crewai-ainative
```

## Quick Start

```python
from crewai_ainative import configure_crew
from crewai import Agent, Task, Crew

configure_crew()  # Auto-provisions free API key, sets env vars

agent = Agent(
    role="Researcher",
    goal="Research AI trends",
    backstory="Expert AI researcher with deep knowledge",
)

task = Task(
    description="Research the latest trends in multi-agent AI systems",
    agent=agent,
    expected_output="A summary of key trends",
)

crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## How It Works

`crewai-ainative` is a companion package (NOT a fork) that configures crewai to use AINative's free, OpenAI-compatible API. It sets the environment variables crewai reads (`OPENAI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_MODEL_NAME`) to route all LLM calls through AINative.

On first use, the package auto-provisions a free API key (72-hour TTL). Claim your account at [ainative.studio/signup](https://ainative.studio/signup) for permanent access.

## Available Models

```python
from crewai_ainative import configure_crew

configure_crew(model="llama")     # meta-llama/Llama-3.3-70B-Instruct (default)
configure_crew(model="qwen")      # qwen3-coder-flash
configure_crew(model="deepseek")  # deepseek-4-flash
configure_crew(model="kimi")      # kimi-k2
```

Or pass any full model ID:

```python
configure_crew(model="meta-llama/Llama-4-Scout-17B-16E-Instruct")
```

## ZeroMemory Integration

Store and recall agent memories across crew runs:

```python
from crewai_ainative import configure_crew, get_memory_config

configure_crew()
memory_config = get_memory_config(entity="my-research-crew")
# memory_config has api_key and memory_api_base for ZeroDB integration
```

## Explicit API Key

```python
configure_crew(api_key="your-key-here")
```

Or set the environment variable:

```bash
export AINATIVE_API_KEY=your-key-here
```

## API Key Resolution Order

1. Explicit `api_key` parameter
2. `AINATIVE_API_KEY` environment variable
3. `ZERODB_API_KEY` environment variable
4. `~/.zerodb/credentials.json` (shared with zerodb ecosystem)
5. Auto-provision via instant-db

## Requirements

- Python >= 3.9
- crewai >= 0.30.0

## License

MIT
