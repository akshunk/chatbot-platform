# Chatbot Platform — Memory File

## Project Goal
Build a conversational chatbot platform under `/workspace/chatbot-platform/` with uncensored content, streaming, personality control, and RAG support. Expose it over the internet from a RunPod instance.

## Constraints
- Uncensored: no topic restrictions, no moralizing, no content policy refusals.
- Streaming via SSE for responses.
- LLM provider swappable via config (Ollama, OpenAI, Groq, OpenRouter).
- Must be accessible from iPhone over internet.
- No signup/login — no auth friction.
- User rejected custom Next.js UI and Open Web UI — prefers minimal, reliable chat interface.

## Active Frontend
- **Gradio ChatInterface** at `apps/ollama-chat/main.py` on port 7860 (production frontend)
- Calls Ollama directly (`/api/chat`), no FastAPI backend in the loop
- SSH tunnel via serveo.net for public access

## History
1. Started with custom HTML/JS proxy (`/tmp/chat_server.py` on port 3000)
2. Switched from localhost.run to serveo.net (localhost.run became unreliable)
3. Replaced custom proxy with Gradio ChatInterface (simpler, no JS/DOM bugs)
4. Fixed 3 Gradio history bugs:
   - **Bug 1**: Role was hardcoded to `"user"` for all history items (fixed by preserving `h["role"]`)
   - **Bug 2**: Content could be a list of structured blocks (`[{"text":"...", "type":"text"}]`) instead of plain string — added `to_str()` recursive flattener
   - **Bug 3**: Message parameter could be a dict `{"text":"...", "type":"text"}` instead of string — `to_str()` extracts `text` key
5. Tests cover all 3 bugs plus edge cases (15 tests total in `apps/ollama-chat/test_main.py`)

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
- `/tmp/gradio_chat.py` — Active running copy (may differ from repo)
- `/tmp/tunnel.url` — Current tunnel URL

## Troubleshooting
- If Gradio crashes: `fuser -k 7860/tcp && python3 apps/ollama-chat/main.py`
- If Ollama model not found: use `llama3.2:3b` (with tag)
- If tunnel dead: kill old serveo process, start new one with `ssh -R 80:localhost:7860 serveo.net`
- Run tests: `cd apps/ollama-chat && python3 -m pytest test_main.py -v`
