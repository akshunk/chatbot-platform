# AGENTS.md

## Project Overview

This is a conversational chatbot platform focused on high-quality conversation,
personality control, and uncensored responses.

## Key Files

- `core/llm/` - LLM provider abstraction (Ollama, OpenAI, Groq, OpenRouter)
- `core/personality/` - Personality definitions (subdirs: `standard/`, plus files at root for default)
- `core/personality/registry.py` - `get_personality_dir(name)`, `list_personalities()` — resolves names→dirs via `config/personality.yaml`
- `core/prompts/` - Prompt templates and assembly
- `core/chat/` - Conversation lifecycle management
- `apps/api/` - FastAPI backend
- `apps/web/` - Next.js frontend
- `apps/ollama-chat/` - Standalone Gradio chat app (direct to Ollama, used as production frontend)
- `config/personality.yaml` - Personality registry (name → directory mapping)
- `data/` - Conversations, feedback, logs

## Running (Active Frontend)

### Quick start (all services)
```bash
cd /workspace/chatbot-platform && ./scripts/start.sh
```

### Manual start
```bash
cd apps/ollama-chat
python3 main.py          # Gradio on port 7860
```

Ollama must be running on port 11434. Tunnel via `ssh -R 80:localhost:7860 serveo.net`.

## Personality System

- `config/personality.yaml` defines available personalities with name, display label, directory, model name, and parameters
- `core/personality/registry.py` caches the YAML; `list_personalities()` returns list for UI (with model), `get_personality_dir(name)` returns the directory, `get_personality_model(name)` returns the Ollama model name
- `core/personality/builder.py` — `PersonalityBuilder(dir)` reads identity.md, tone.md, boundaries.md, examples.md → system prompt
- Each personality is a subdirectory under `core/personality/` with those 4 files
- The Gradio app injects the system prompt as a `system` role message on every turn
- Each personality specifies its own Ollama model via `model` field in config (default: `llama3.2:3b`, companion uses `dolphin-llama3:8b`)
- The Gradio app reads the per-personality model at chat time, not a hardcoded MODEL variable
- Personalities: `default` (uncensored Nova), `standard` (safe ChatGPT-style), `experimental` (empty)

## Services & Scripts

- `scripts/start.sh` — Single launcher: checks/starts Ollama, pulls model if needed, starts Gradio on 7860, starts autossh tunnel via serveo.net. Ctrl+C stops all.
- `scripts/tunnel.sh` — Manages SSH tunnel (start/stop/status). Uses autossh for auto-reconnect. Saves URL to `/tmp/tunnel.url`.

## Tunnel & iPhone Access

- **Primary service**: serveo.net (fallback: `TUNNEL_HOST=nokey@localhost.run`)
- URL changes each connection (ephemeral). Get current: `cat /tmp/tunnel.url`
- If iPhone shows "page not reachable", first check local Gradio: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7860`
  - Not `200`? → restart Gradio (likely crashed) — `fuser -k 7860/tcp && python3 apps/ollama-chat/main.py`
  - `200`? → tunnel issue — restart tunnel: `./scripts/tunnel.sh restart`
  - Hard refresh on iPhone (private tab) — Safari caches Gradio aggressively

## First-Time UI Setup

```bash
pip install gradio httpx pyyaml          # deps (once)
ollama pull llama3.2:3b                    # default model (once, ~2GB)
./scripts/start.sh                         # start everything
```

## Testing

```bash
cd apps/ollama-chat && python3 -m pytest test_main.py -v   # 15 tests
cd /workspace/chatbot-platform && python3 -m pytest apps/ollama-chat/test_main.py -v
```

## Architecture

- Frontend sends messages via SSE streaming to the API
- API assembles prompts from personality + history + user message
- LLM provider abstraction allows switching models without changing code
- Conversations are stored as JSON/JSONL in data/conversations/
- Feedback is stored in data/feedback/

## Design Principles

1. Keep UI, chat logic, prompts, and model calls separate
2. LLM provider must be replaceable via config
3. Prompts are editable files, not hardcoded strings
4. Personality is a first-class feature
5. Every response should be traceable to prompt, context, and model

## Uncensored Design

The personality (`core/personality/identity.md`, `boundaries.md`) explicitly
removes content restrictions. The assistant will discuss any topic without
moralizing or refusing to engage.
