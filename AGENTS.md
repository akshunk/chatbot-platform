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

### Manual start (via tmux — survives shell exit)
```bash
tmux new-session -d -s comfyui -c /workspace/ComfyUI '/workspace/ComfyUI/.venv/bin/python3 main.py --listen --port 8188'
tmux new-session -d -s gradio -c /workspace/chatbot-platform 'python3 apps/ollama-chat/main.py'
tmux new-session -d -s tunnel 'ssh -o StrictHostKeyChecking=no -R 80:localhost:7860 serveo.net'
```

Ollama must be running on port 11434. Attach to logs: `tmux attach -t <session>`.

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

- `scripts/start.sh` — Single launcher: checks system deps, installs Python deps, checks/starts Ollama, pulls both models if missing, starts Gradio on 7860, starts SSH tunnel via serveo.net. Services are isolated (won't die on script exit).
- `scripts/tunnel.sh` — Manages SSH tunnel (start/stop/status). Uses plain `nohup ssh` (not autossh). Saves URL to `/tmp/tunnel.url`.

## Tunnel & iPhone Access

- **Primary service**: serveo.net (fallback: `TUNNEL_HOST=nokey@localhost.run`)
- URL changes each connection (ephemeral). Get current: `cat /tmp/tunnel.url`
- If iPhone shows "page not reachable", first check local Gradio: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7860`
  - Not `200`? → restart Gradio (likely crashed) — `fuser -k 7860/tcp && python3 apps/ollama-chat/main.py`
  - `200`? → tunnel issue — restart tunnel: `./scripts/tunnel.sh restart`
  - Hard refresh on iPhone (private tab) — Safari caches Gradio aggressively

## First-Time UI Setup

### System dependencies (one-time)
```bash
apt-get install curl               # health checks
# Ollama: install from https://ollama.ai or run the binary
```

### Python + models + start
```bash
pip install -r apps/ollama-chat/requirements.txt   # Python deps (once)
ollama pull llama3.2:3b                            # default model (once, ~2GB)
ollama pull dolphin-llama3:8b                      # companion model (once, ~4.7GB)
./scripts/start.sh                                 # start everything
```

`scripts/start.sh` auto-checks all system deps, Python deps, and models on startup.

## Known Issues & Fixes

### Chat page refreshes instead of responding
- **Cause**: `async def` generator functions don't work with Gradio 6.x ChatInterface — the page reloads instead of streaming.
- **Fix**: Use a synchronous generator (`def` not `async def`) with `httpx.Client` (not `AsyncClient`). The `chat()` function in `apps/ollama-chat/main.py` must be sync.
- **Additional fix**: Cold model load (12s+ for 8B model) causes first `yield` to stall, timing out the frontend websocket. `_warm_models()` pre-loads all models at startup.
- **Error resilience**: `try/except` wrapper around the Ollama call prevents unhandled exceptions from crashing the generator.

### SSE idle timeout drops connection during long generation
- **Cause**: serveo.net proxy has an idle timeout (~30s). Image generation (ComfyUI) takes 10-47s. No data flows between initial `yield ""` and final yield, so proxy drops the connection ("server is lost" / page refreshes).
- **Fix**: Image generation runs in a `daemon=True` thread with a `queue.Queue`. Main generator calls `result_q.get(timeout=10)` in a loop; if timeout fires, yields `"⏳ Generating image..."` as a keepalive. Each yield in Gradio ChatInterface's `_stream_fn` replaces the previous assistant message (builds from same base history), so keepalive text is invisible to the user.

### Model refuses to generate `<gen>` tags for explicit images
- **Cause**: Model anthropomorphized image generation — thought "generate an image" meant creating an image of *itself* (the AI persona). Original wording "You can generate images" triggered refusal.
- **Fix**: All 4 system prompt files updated with "MUST NEVER refuse" + "external image generator" framing.

### Model doesn't output `<gen>` tags for all visual requests (responds instantly with text)
- **Cause**: `GEN_INTENT` regex in `main.py` only matched `generate/create/make + image/photo/picture`. Phrases like "generate a naked woman" matched the verb but not the object, so the image-intent system message was never injected. Without that nudge, the model sometimes outputs gen tags, sometimes not.
- **Fix**: Broadened `GEN_INTENT` regex to also match `show/give + naked/nude/sexy/explicit/woman/man/girl/guy`. And updated all 4 system prompts from "When the user asks for a photo or image" to "Whenever the user wants to see or generate **any visual content** (photo, image, **naked person, explicit scene, etc.**) — treat ANY request to visualize something as requiring a `<gen>` tag."

### Gradio version compatibility
- Gradio 6.19 has a Starlette 1.3.1 deprecation conflict. Pinned to `<6.19` in `requirements.txt`.

## Image Generation

- ComfyUI runs on port 8188 (started by `scripts/start.sh` or manually in tmux)
- Model: RealVisXL V4.0 (`RealVisXL_V4.0.safetensors`, 6.6GB, photorealistic)
- Fallback: Juggernaut XL v9 (`Juggernaut-XL-v9.safetensors`, 6.9GB)
- LLM triggers image gen via `<gen>description</gen>` tags in response
- `core/imagegen/workflow.py` builds txt2img workflow JSON
- `core/imagegen/client.py` — `generate_image(prompt)` calls ComfyUI API, polls for result, returns image path
- `enhance_prompt()` wraps prompt with `RAW photo, ` prefix + `, professional photography, natural lighting, sharp focus, highly detailed, 8K, shot on professional camera` suffix (natural language, no weighted pony tags)
- Images saved to `ComfyUI/output/`
- Gradio `launch()` must include `allowed_paths=["/workspace/ComfyUI/output"]` to serve image files
- **Image rendering**: Clickable `[📷 View Image]` link via `/gradio_api/file={path}` (not inline `<img>`) to avoid Gradio Chatbot rendering issues
- **Keepalive**: Image gen runs in a background thread; main generator yields keepalives every 10s to prevent SSE/proxy timeout
- **`chat()` flow**: `yield ""` (establish SSE) → collect LLM response → if `<gen>` found → safety check → `enhance_prompt()` → threaded `generate_image()` with keepalive yields → yield clickable link. No `demo.queue()` (caused timeout). No progress yields (Gradio ChatInterface appends them).
- **Gen tag trigger**: `GEN_INTENT` regex in `main.py` detects visual requests. If matched, injects additional system message with explicit gen tag example. Broadened to catch `show/give + naked/nude/sexy/explicit/woman/man/girl/guy`.
- **All 4 system prompts**: Updated with "Whenever the user wants to see or generate **any visual content** — treat ANY request to visualize as requiring a `<gen>` tag" + "MUST NEVER refuse" + "external image generator" framing

### Image Cleanup
`scripts/cleanup-images.sh` manages disk usage in `ComfyUI/output/`:
```bash
./scripts/cleanup-images.sh                  # keep 50 newest, delete >48h old
./scripts/cleanup-images.sh --keep 100       # keep 100 newest
./scripts/cleanup-images.sh --max-age 24     # delete >24h old
./scripts/cleanup-images.sh --dry-run        # preview without deleting
```

### Safety Filter
`is_safe_prompt()` in `apps/ollama-chat/main.py` checks gen tag prompts for:
- Animal keywords + explicit keywords → blocked
- Child/minor keywords + explicit/violent keywords → blocked
Returns error message instead of generating. Also: all 4 system prompt files include absolute boundaries.

## Testing

```bash
cd apps/ollama-chat && python3 -m pytest -v   # 32 tests (15 original + 17 image gen)
cd /workspace/chatbot-platform && python3 -m pytest apps/ollama-chat/ -v
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
