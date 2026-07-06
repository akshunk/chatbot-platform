# Chatbot Platform — Memory File

## Project Goal
Build a conversational chatbot platform under `/workspace/chatbot-platform/` with uncensored content, streaming, personality control, and RAG support. Expose it over the internet from a RunPod instance.

## Constraints
- Uncensored by default but personality-switchable (standard/safe persona also available).
- Streaming via SSE for responses.
- LLM provider swappable via config (Ollama, OpenAI, Groq, OpenRouter).
- Must be accessible from iPhone over internet.
- No signup/login — no auth friction.
- User rejected custom Next.js UI and Open Web UI — prefers minimal, reliable chat interface.

## Active Frontend
- **Gradio ChatInterface** at `apps/ollama-chat/main.py` on port 7860 (production frontend)
- Calls Ollama directly (`/api/chat`), no FastAPI backend in the loop
- SSH tunnel via serveo.net for public access
- Personality selector in an open accordion below the chat (via `additional_inputs`)

## History
1. Started with custom HTML/JS proxy (`/tmp/chat_server.py` on port 3000)
2. Switched from localhost.run to serveo.net (localhost.run became unreliable)
3. Replaced custom proxy with Gradio ChatInterface (simpler, no JS/DOM bugs)
4. Fixed 3 Gradio history bugs:
   - **Bug 1**: Role was hardcoded to `"user"` for all history items (fixed by preserving `h["role"]`)
   - **Bug 2**: Content could be a list of structured blocks (`[{"text":"...", "type":"text"}]`) instead of plain string — added `to_str()` recursive flattener
   - **Bug 3**: Message parameter could be a dict `{"text":"...", "type":"text"}` instead of string — `to_str()` extracts `text` key
5. Tests cover all 3 bugs plus edge cases (15 tests in `apps/ollama-chat/test_main.py`)
6. Added **standard/safe personality** (identity, tone, boundaries with 10 guidelines, examples)
7. Added `core/personality/registry.py` — resolves personality names to directories via `config/personality.yaml`
8. Wired personality selection into Gradio UI via `additional_inputs` with open accordion
9. System prompt from selected personality injected as `system` role message on every turn
10. Added **per-personality model selection** — each personality specifies its own Ollama model in `config/personality.yaml`, `registry.py` exposes `get_personality_model()`, Gradio uses it at runtime
11. Switched Companion to `dolphin-llama3:8b` (uncensored, better for explicit content). Nova/Standard remain on `llama3.2:3b`

## Personality System
| Name | Key | Directory | Description | Model |
|------|-----|-----------|-------------|-------|
| Nova | `default` | `core/personality/` | Unfiltered, direct, intelligent assistant (uncensored) | `llama3.2:3b` |
| Standard | `standard` | `core/personality/standard/` | Helpful, harmless, honest — ChatGPT-style with safety guidelines | `llama3.2:3b` |
| Companion | `nsfw` | `core/personality/nsfw/` | Uncensored adult companion, sexually open, direct | `dolphin-llama3:8b` |
| Nova (Experimental) | `experimental` | `experiments/personalities/experimental/` | Empty (placeholder) | `llama3.2:3b` |

## Running Services
| Service | Port | How to start |
|---------|------|-------------|
| Gradio chat | 7860 | `python3 apps/ollama-chat/main.py` |
| Ollama | 11434 | `ollama serve` (should already be running) |
| SSH tunnel (serveo) | varies | `scripts/tunnel.sh start` |

## Quick Start (all services)
```bash
./scripts/start.sh
```
Single command: checks/starts Ollama, pulls model if missing, kills old Gradio and starts fresh, starts autossh tunnel via serveo.net, prints URLs. Ctrl+C stops all.

## Scripts
- `scripts/start.sh` — All-in-one launcher (Ollama → model → Gradio → tunnel)
- `scripts/tunnel.sh` — Tunnel manager with start/stop/status. Uses autossh (auto-reconnect). Accepts `TUNNEL_PORT` and `TUNNEL_HOST` env vars. URL saved to `/tmp/tunnel.url`.

## Tunnel

### Service
- **Primary**: serveo.net (more reliable than localhost.run)
- **Fallback**: localhost.run — `TUNNEL_HOST=nokey@localhost.run ./scripts/tunnel.sh restart`

### How it works
- `autossh` creates a reverse SSH tunnel: remote port 80 → localhost:7860
- Tunnel auto-reconnects if dropped (autossh monitors the connection)
- Each connection gets a new random URL (ephemeral — no custom domain)

### First time setup
```bash
ssh -o StrictHostKeyChecking=no serveo.net
# Accept the host key, then Ctrl+C (host is now in known_hosts)
```

### Quick commands
| Action | Command |
|--------|---------|
| Start tunnel | `./scripts/tunnel.sh start` |
| Stop tunnel | `./scripts/tunnel.sh stop` |
| Restart tunnel | `./scripts/tunnel.sh restart` |
| Check status | `./scripts/tunnel.sh status` |
| Get current URL | `cat /tmp/tunnel.url` |

### Tunnel troubleshooting

**Page not reachable on iPhone:**
1. First check the local app: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:7860` — should return `200`. If not, restart Gradio.
2. Check tunnel status: `cat /tmp/tunnel.url` — if empty or stale, restart tunnel.
3. Check autossh is running: `pgrep -f autossh`
4. Try serveo directly (bypass autossh) to see real errors:
   ```bash
   pkill -f "autossh.*serveo"; sleep 1
   ssh -o StrictHostKeyChecking=no -R 80:localhost:7860 serveo.net
   ```
5. If serveo fails, switch to localhost.run:
   ```bash
   TUNNEL_HOST=nokey@localhost.run ./scripts/tunnel.sh restart
   ```
6. Hard refresh on iPhone (Settings → Safari → Clear History and Website Data, or use private tab) — Gradio caches aggressively.

**Common causes of "page not reachable":**
- Gradio crashed but tunnel is still up (tunnel points at nothing)
- Tunnel process died (autossh should restart it, but may take ~30s)
- serveo.net is temporarily down (use localhost.run fallback)
- iPhone cached an old Gradio page — Safari aggressively caches; use private tab or clear history

## Important Files
- `/workspace/chatbot-platform/apps/ollama-chat/main.py` — Gradio chat app
- `/workspace/chatbot-platform/apps/ollama-chat/test_main.py` — Tests (15 tests)
- `/workspace/chatbot-platform/core/personality/registry.py` — Name→dir resolver, `get_personality_model()`
- `/workspace/chatbot-platform/config/personality.yaml` — Personality definitions with model per personality
- `/workspace/chatbot-platform/core/personality/standard/` — Safe persona files
- `/workspace/chatbot-platform/scripts/start.sh` — All-in-one launcher (Ollama → model → Gradio → tunnel)
- `/workspace/chatbot-platform/scripts/tunnel.sh` — Tunnel manager (start/stop/status, autossh, serveo.net)
- `/tmp/gradio_chat.py` — Active running copy (may differ from repo)
- `/tmp/tunnel.url` — Current tunnel URL

## Setting Up the UI (First Time)

### Prerequisites (already installed on this machine)
- Python 3.12+, `gradio`, `httpx`, `pyyaml` (`pip install gradio httpx pyyaml`)
- Ollama (`/usr/local/bin/ollama`)

### Starting from a clean session
```bash
# 1. Start Ollama (if not running)
ollama serve &
sleep 2

# 2. Pull the default model (first time only — 2GB download)
ollama pull llama3.2:3b

# 3. Start the chat UI
cd /workspace/chatbot-platform
python3 apps/ollama-chat/main.py

# 4. In another terminal, start the tunnel
./scripts/tunnel.sh start
```

### Or use the all-in-one command:
```bash
cd /workspace/chatbot-platform && ./scripts/start.sh
```

### UI features
- **Personality selector**: Open accordion below the chat — choose Nova, Standard, Companion, or Experimental
- Each personality has its own system prompt (loaded from Markdown files) and model
- Chat messages are shown in the browser session only (lost on refresh in Phase 1)

### Accessing from iPhone
- Open the tunnel URL in Safari (URL in `/tmp/tunnel.url`)
- Add to Home Screen for app-like access
- If page loads but chat doesn't respond, check that Ollama has the model loaded

## Known Issues
- Chat history not persisted (browser memory only — lost on refresh)
- Personality selector is in an accordion below the chat (Gradio limitation with `additional_inputs`)
- `experimental` personality directory is empty

## Fixed Issues
### Async generator → page refresh (gradio 6.x)
- **Bug**: `async def chat()` with `yield` in Gradio 6.19 ChatInterface caused page to refresh on message send instead of streaming response.
- **Root cause**: Gradio 6.x doesn't properly handle async generators — it hangs and reloads the UI.
- **Fix**: Changed `chat()` to a synchronous generator (`def` instead of `async def`) using `httpx.Client` instead of `httpx.AsyncClient`. All 15 tests pass.

## Troubleshooting
- If Gradio crashes: `fuser -k 7860/tcp && python3 apps/ollama-chat/main.py`
- If Ollama model not found: use `llama3.2:3b` (with tag). Companion needs `dolphin-llama3:8b`
- If tunnel dead: `./scripts/tunnel.sh restart` (autossh reconnects automatically)
- If everything needs a restart: `./scripts/start.sh` (handles all services, Ctrl+C to stop)
- Run tests: `cd apps/ollama-chat && python3 -m pytest test_main.py -v`
- Hard refresh (Cmd+Shift+R) if UI looks stale — Gradio caches aggressively
