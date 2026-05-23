# Deep Notes

Semantic search for your Obsidian vault. Ask natural language questions about your notes and get answers grounded in your own writing, with source references.

## Architecture

```
Obsidian Vault (.md files)
    → Frontmatter parsing (extract tags)
    → Chunking (sentence / token / markdown)
    → Embedding (Ollama BGE-m3 / OpenAI)
    → Vector Store (Qdrant)
    → Query: retrieve chunks → LLM generates answer with citations
```

Every component is **swappable via environment variables** — no code changes needed to switch embedding models, vector databases, chunking strategies, or LLM providers.

## Tech Stack

### Orchestrator: LlamaIndex

[LlamaIndex](https://docs.llamaindex.ai/) is the RAG orchestration framework that ties everything together — document loading, chunking, embedding, vector storage, and query synthesis. Its plugin architecture makes every component swappable without changing application code.

### Vector Database: Qdrant

[Qdrant](https://qdrant.tech/) stores document embeddings and performs similarity search. It runs locally via Docker with persistent storage, exposes a dashboard at `http://localhost:6333/dashboard`, and supports filtering by metadata (tags, folders) for future use.

**Alternatives:** Chroma, Weaviate, Pinecone, Milvus — add a new `case` in `components/vector_store.py`.

### Embedding Models

Default: **BGE-m3** via [Ollama](https://ollama.com) — runs locally, free, multilingual, strong retrieval performance.

| Provider | Models | Cost | Setup |
|---|---|---|---|
| **Ollama** (default) | bge-m3, nomic-embed-text, mxbai-embed-large | Free (local) | `ollama pull <model>` |
| **OpenAI** | text-embedding-3-small, text-embedding-3-large | Pay-per-token | API key required |

Change with `EMBED_PROVIDER` and `EMBED_MODEL` in `.env`.

### LLM Providers

Default: **Ollama** with llama3.2 — fully local, free, no API key needed.

| Provider | Models | Cost | Setup |
|---|---|---|---|
| **Ollama** (default) | llama3.2, mistral, gemma2, phi3 | Free (local) | `ollama pull <model>` |
| **OpenRouter** | Claude, GPT-4, Llama, Gemma, Mistral, 200+ models | Pay-per-token (some free) | API key from [openrouter.ai](https://openrouter.ai) |
| **OpenAI** | gpt-4o, gpt-4o-mini | Pay-per-token | API key required |

Change with `LLM_PROVIDER` and `LLM_MODEL` in `.env`.

### Chunking Strategies

| Strategy | Description | Best for |
|---|---|---|
| **sentence** (default) | Splits on sentence boundaries | General purpose, preserves sentence context |
| **token** | Splits on token count | Precise control over chunk size |
| **markdown** | Splits on markdown headers/sections | Well-structured notes with headings |

Change with `CHUNK_STRATEGY`, `CHUNK_SIZE`, and `CHUNK_OVERLAP` in `.env`.

## Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- [Ollama](https://ollama.com) (for local embeddings)

## Setup

```bash
# 1. Clone and install
git clone https://github.com/yourusername/deep-notes.git
cd deep-notes
pip install -r requirements.txt

# 2. Start Qdrant
docker compose up -d

# 3. Pull the embedding model
ollama pull bge-m3

# 4. Configure
cp .env.example .env
# Edit .env — set VAULT_PATH and OPENROUTER_API_KEY at minimum
```

## Usage

### Index your vault

```bash
python -m deep_notes.ingest
```

### Run the UI

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), then ask questions about your notes.

## Configuration

All settings are in `.env`. Key options:

| Variable | Default | Options |
|---|---|---|
| `EMBED_PROVIDER` | `ollama` | `ollama`, `openai` |
| `EMBED_MODEL` | `bge-m3` | Any model supported by the provider |
| `VECTOR_STORE_PROVIDER` | `qdrant` | `qdrant` |
| `CHUNK_STRATEGY` | `sentence` | `sentence`, `token`, `markdown` |
| `CHUNK_SIZE` | `512` | Any integer |
| `LLM_PROVIDER` | `openrouter` | `openrouter`, `openai`, `ollama` |
| `LLM_MODEL` | `anthropic/claude-sonnet-4` | Any model supported by the provider |

## Project Structure

```
deep_notes/
├── config.py              # Pydantic settings — all knobs in one place
├── components/
│   ├── embeddings.py      # Embedding model factory
│   ├── vector_store.py    # Vector store factory
│   ├── llm.py             # LLM factory
│   └── chunking.py        # Chunking strategy factory
├── ingest.py              # Vault loading + ingestion pipeline
├── query.py               # Retrieval + answer generation
app.py                     # Streamlit UI
```

## Adding a new provider

1. Add a new `case` to the relevant factory in `deep_notes/components/`
2. Add the LlamaIndex integration package to `requirements.txt`
3. Add any new env vars to `config.py` and `.env.example`
