# Prompt Design

## Philosophy

The prompt is not a single monolithic string. It is assembled from modular
components that can be edited independently.

## Components

### 1. System Rules (`core/prompts/system.md`)

A short base instruction that establishes the assistant's role. This is the
foundation that all other components build upon.

### 2. Personality (`core/personality/`)

The personality is the chatbot's identity. It consists of:

- **identity.md** - Who the assistant is, what it stands for
- **tone.md** - How it speaks, what to avoid
- **boundaries.md** - What it will/won't do
- **examples.md** - Example interactions showing desired style

These are combined by `PersonalityBuilder.build_system_prompt()`.

### 3. Conversation History (`core/prompts/conversation.md`)

Formatted as alternating User/Assistant messages. Provides context for the
current turn.

### 4. RAG Context (`core/prompts/rag.md`)

Sources from the knowledge base, with citations. Only included when RAG is
enabled and relevant content is found.

### 5. Web Search Context (`core/prompts/search.md`)

Recent information from web search. Only included when web search is triggered.

### 6. Memory Context (`core/prompts/memory.md`)

Relevant information from past conversations. Only included when memory is
available.

### 7. User Message

The current user input, always included as the final message.

## Assembly Order

The `PromptBuilder.build_messages()` method assembles these in order:

```
[
  {"role": "system", "content": system_rules + personality},
  {"role": "system", "content": conversation_history},
  {"role": "system", "content": rag_context},
  {"role": "system", "content": search_context},
  {"role": "system", "content": memory_context},
  {"role": "user", "content": user_message},
]
```

## Uncensored Design

The personality files explicitly instruct the assistant to:

- Discuss any topic without refusal
- Avoid moralizing or lecturing
- Be direct and intellectually honest
- Never use hedging phrases like "As an AI model..."

This is enforced via the `boundaries.md` and `identity.md` files.

## Experimentation

New prompts can be tested by:

1. Creating a new personality directory under `experiments/personalities/`
2. Adding it to `config/personality.yaml`
3. Switching the personality in the API or UI
