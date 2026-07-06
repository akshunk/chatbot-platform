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
| SSH tunnel (serveo) | varies | `ssh -R 80:localhost:7860 serveo.net` |

## Tunnel
- Service: serveo.net (not localhost.run)
- URL saved to `/tmp/tunnel.url`
- Auto-restart not yet set up (run manually or via cron)

## Important Files
- `/workspace/chatbot-platform/apps/ollama-chat/main.py` — Gradio chat app
- `/workspace/chatbot-platform/apps/ollama-chat/test_main.py` — Tests (15 tests)
- `/workspace/chatbot-platform/core/personality/registry.py` — Name→dir resolver, `get_personality_model()`
- `/workspace/chatbot-platform/config/personality.yaml` — Personality definitions with model per personality
- `/workspace/chatbot-platform/core/personality/standard/` — Safe persona files
- `/tmp/gradio_chat.py` — Active running copy (may differ from repo)
- `/tmp/tunnel.url` — Current tunnel URL

## Known Issues
- Chat history not persisted (browser memory only — lost on refresh)
- Personality selector is in an accordion below the chat (Gradio limitation with `additional_inputs`)
- No auto-restart script for the tunnel
- `experimental` personality directory is empty

## Troubleshooting
- If Gradio crashes: `fuser -k 7860/tcp && python3 apps/ollama-chat/main.py`
- If Ollama model not found: use `llama3.2:3b` (with tag). Companion needs `dolphin-llama3:8b`
- If tunnel dead: kill old serveo process, start new one with `ssh -R 80:localhost:7860 serveo.net`
- Run tests: `cd apps/ollama-chat && python3 -m pytest test_main.py -v`
- Hard refresh (Cmd+Shift+R) if UI looks stale — Gradio caches aggressively
