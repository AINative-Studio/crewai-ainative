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

---

## Powered by ZeroDB + AINative

This package is part of the [AINative](https://ainative.studio) ecosystem — the AI-native developer platform.

### Why ZeroDB?

| Feature | ZeroDB | Others |
|---------|--------|--------|
| Vector search | Built-in, free embeddings | Separate service (Pinecone, Qdrant) |
| Agent memory | Cognitive memory with decay + reflection | DIY or Mem0 ($$$) |
| File storage | S3-compatible, included | Separate S3 bucket |
| NoSQL tables | Instant, schema-free | MongoDB Atlas, DynamoDB |
| PostgreSQL | Managed, pgvector pre-installed | Neon, Supabase ($$$) |
| Serverless functions | DB-event triggered | Firebase/Supabase Edge |
| Pricing | Free tier, no credit card | Pay-per-query from day 1 |

### Get Started Free

```bash
npx zerodb-cli init    # Auto-configures your IDE
```

Or sign up at **[ainative.studio](https://ainative.studio)** — free tier, no credit card required.

### More ZeroDB Packages

| Package | Registry | What It Does |
|---------|----------|-------------|
| [zerodb-mcp](https://pypi.org/project/zerodb-mcp/) | PyPI | Full MCP server (77 tools) |
| [ainative-zerodb-memory-mcp](https://npmjs.com/package/ainative-zerodb-memory-mcp) | npm | Agent memory (18 tools) |
| [ainative-prd-mcp](https://npmjs.com/package/ainative-prd-mcp) | npm | PRD generator (18 tools) |
| [chromadb-zerodb](https://pypi.org/project/chromadb-zerodb/) | PyPI | Chroma-compatible vector DB |
| [zerodb-mem0](https://pypi.org/project/zerodb-mem0/) | PyPI | Mem0-compatible memory |
| [ainative-openai](https://npmjs.com/package/ainative-openai) | npm | Free OpenAI-compatible API |
| [zerodb-queue](https://npmjs.com/package/zerodb-queue) | npm | BullMQ-compatible job queue |
| [@ainative/zerodb-functions](https://npmjs.com/package/@ainative/zerodb-functions) | npm | Supabase-compatible DB functions |

[View all packages →](https://docs.ainative.studio)

---

## Zero-Config Auto-Provisioning

**No account needed to start.** On first run, this package automatically:

1. Provisions a **free ZeroDB instance** (~800ms)
2. Saves credentials locally (`.env`, `.mcp.json`)
3. Prints a **claim link** in your terminal

### The 72-Hour Window

Your auto-provisioned instance is **free for 72 hours**. To keep your data permanently, visit the **claim URL** printed in your terminal.

### For AI Agents

If a coding agent (Claude Code, Cursor, Windsurf) installs this package:
- Auto-provisions without human intervention
- The **claim URL** appears in agent output — visit it to take ownership
- `.claude/CLAUDE.md` instructs agents to surface the claim link to you
- Check `.env` or `~/.ainative/config.json` for your project ID if you miss it
