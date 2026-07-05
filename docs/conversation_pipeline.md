# Conversation Pipeline

The conversation pipeline defines how a user message flows through the system
to produce a response.

## Pipeline Steps

```
User message
    │
    ▼
1. Load conversation history
    │
    ▼
2. (Phase 2) Classify request
    │
    ▼
3. (Phase 3) Retrieve memory
    │
    ▼
4. (Phase 2) Retrieve knowledge via RAG
    │
    ▼
5. (Phase 3) Run web search if needed
    │
    ▼
6. Assemble personality + prompt
    │
    ▼
7. Call LLM
    │
    ▼
8. Stream response
    │
    ▼
9. Save conversation
    │
    ▼
10. Collect feedback
```

## Current Implementation (Phase 1)

Steps 1, 6, 7, 8, 9, and 10 are implemented. Steps 2-5 are stubs.

### Step 1: Load History

The API loads the conversation's message list from `data/conversations/{id}.jsonl`.

### Step 6: Assemble Prompt

The `PromptBuilder` combines:
- System prompt (from `core/prompts/system.md`)
- Personality (identity + tone + boundaries + examples)
- Conversation history (formatted as alternating user/assistant messages)
- User message

### Step 7: Call LLM

The `ResponseGenerator` formats the messages and calls the configured LLM provider.
The provider is selected by `LLMRouter` based on config.

### Step 8: Stream Response

Responses are streamed via Server-Sent Events (SSE). Each chunk is sent as
a JSON-encoded event with the partial content.

### Step 9: Save

The user message is saved before generation. The assistant response is saved
after streaming completes.

### Step 10: Feedback

Users can submit thumbs up/down feedback on assistant messages. This is stored
in `data/feedback/` for future evaluation.

## Phase 2 Additions

- Request classification to determine if RAG is needed
- RAG retrieval from knowledge base
- Citation metadata in responses

## Phase 3 Additions

- Memory retrieval from past conversations
- Web search when query needs freshness
- Full evaluation pipeline
