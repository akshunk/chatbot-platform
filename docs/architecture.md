# Architecture

## Overview

The chatbot platform follows a clean separation of concerns with three main
application layers and core business logic modules.

```
┌─────────────────────┐
│     apps/web        │  Next.js frontend
│   (React, Tailwind) │
└────────┬────────────┘
         │ SSE / REST
         ▼
┌─────────────────────┐
│     apps/api        │  FastAPI backend
│  (Python, Pydantic) │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│     core/           │  Business logic
│  chat, llm, prompts │
│  personality, ...   │
└─────────────────────┘
```

## Core Modules

### `core/llm`

Abstracts LLM providers behind a common interface. Supports:

- **Ollama** - Local models via Ollama API
- **OpenAI-compatible** - Any OpenAI API-compatible provider
- **Groq** - Groq's fast inference API
- **OpenRouter** - Multi-model router API

The `LLMRouter` selects the active provider based on configuration.

### `core/personality`

Defines the chatbot's identity as editable Markdown files. The `PersonalityBuilder`
assembles identity, tone, boundaries, and examples into a system prompt.

### `core/prompts`

Template-based prompt assembly. The `PromptBuilder` composes the final prompt from:

1. System rules + personality
2. Conversation history
3. RAG context (when available)
4. Web search context (when available)
5. Memory context (when available)
6. User message

### `core/chat`

Manages the conversation lifecycle:

- `Conversation` - Conversation metadata model
- `Message` - Individual message model
- `ConversationHistory` - Persistence layer (JSON/JSONL files)
- `ContextBuilder` - Builds LLM context from components
- `ResponseGenerator` - Calls the LLM and returns/streams responses

## Data Flow

```
User → Web UI → API → ContextBuilder → LLM → Stream → Web UI
                         ↑
                  Personality + History
```

## Storage

Conversations are stored as JSON files (metadata) and JSONL files (messages)
in `data/conversations/`. No database is required for Phase 1.
