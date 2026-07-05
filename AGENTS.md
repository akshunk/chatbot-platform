# AGENTS.md

## Project Overview

This is a conversational chatbot platform focused on high-quality conversation,
personality control, and uncensored responses.

## Key Files

- `core/llm/` - LLM provider abstraction (Ollama, OpenAI, Groq, OpenRouter)
- `core/personality/` - Chatbot identity, tone, boundaries
- `core/prompts/` - Prompt templates and assembly
- `core/chat/` - Conversation lifecycle management
- `apps/api/` - FastAPI backend
- `apps/web/` - Next.js frontend
- `config/` - YAML configuration files
- `data/` - Conversations, feedback, logs

## Running

```bash
# Start API
uvicorn apps.api.main:app --reload --port 8000

# Start Web (in apps/web/)
npm run dev

# With Docker
docker compose up
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
