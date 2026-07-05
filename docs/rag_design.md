# RAG Design

> Phase 2 feature - not yet implemented.

## Planned Architecture

```
Document Upload
    │
    ▼
Chunking (chunker.py)
    │
    ▼
Embedding (embedder.py)
    │
    ▼
Vector Store (ChromaDB → pgvector)
    │
    ▼
Retrieval (retriever.py)
    │
    ▼
Reranking (reranker.py)
    │
    ▼
Citation Building (citation_builder.py)
```

## Components

### Chunker

Splits documents into overlapping chunks of configurable size. Supports
Markdown, text, and PDF files.

### Embedder

Generates embeddings using a local model (via Ollama) or API. Stores vectors
for similarity search.

### Retriever

Finds the top-k most relevant chunks for a given query using cosine similarity.

### Reranker

Optionally re-ranks results using a cross-encoder for better precision.

### Citation Builder

Formats retrieved chunks with source information for display in responses.

## Storage

- Phase 2: ChromaDB (simple, file-based)
- Future: PostgreSQL + pgvector (more scalable)
