# Chatbot Platform

A conversational chatbot platform focused on high-quality conversation,
personality control, RAG-based knowledge, and uncensored responses.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- [Ollama](https://ollama.ai) (for local LLM)

### 1. Start Ollama and pull a model

```bash
ollama pull llama3.2
```

### 2. Start the API

```bash
cd chatbot-platform
pip install -r apps/api/requirements.txt
uvicorn apps.api.main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

### With Docker

```bash
docker compose up
```

## Features

- Streaming responses via SSE
- Personality-driven system prompts (identity, tone, boundaries)
- Multiple LLM providers (Ollama, OpenAI, Groq, OpenRouter)
- Conversation history and management
- Message feedback (thumbs up/down)
- Response regeneration

## Project Structure

```
apps/web/          - Next.js frontend
apps/api/          - FastAPI backend
core/chat/         - Conversation lifecycle
core/llm/          - LLM provider abstraction
core/personality/  - Chatbot identity and style
core/prompts/      - Prompt templates
config/            - YAML configuration
data/              - Conversations, feedback, logs
```

## Configuration

Edit files in `config/` to change providers, models, and personality settings.

## Phases

- **Phase 1** (current): Core chat, streaming, personality, one LLM provider
- **Phase 2**: RAG with document ingestion, knowledge retrieval
- **Phase 3**: Memory, web search, evaluation

## License

MIT
