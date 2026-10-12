# Embedding Kit

Reusable Python embedding provider configuration for **OpenAI**, **OpenRouter**, and **Ollama**, powered by LangChain's existing `Embeddings` interface. This package does not store vectors, build RAG pipelines, or depend on FastAPI.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Development with uv

From the `embedding-kit` directory:

```bash
uv sync --extra all --extra test
uv run pytest
uv run ruff check .
uv build
```

No credentials are needed for unit tests; production calls require valid credentials or a running Ollama service.

## Install in another project

From your consuming project's directory, add this Git repository **subdirectory**:

```bash
uv add "hamresan-embedding-kit[openai] @ git+https://github.com/hamresan/shared-packages.git@feat/embedding-kit#subdirectory=embedding-kit"
```

Replace `openai` with `openrouter`, `ollama`, or `all` as needed. For reproducible deployments, pin a commit SHA or a released tag instead of a moving branch. After merging to main, update the Git ref appropriately.

To install from a local checkout:

```bash
uv add "./shared-packages/embedding-kit[all]"
```

Adjust the relative path for your checkout.

## OpenAI

```bash
export OPENAI_API_KEY="your-key"
```

```python
from embedding_kit import EmbeddingSettings, create_embeddings

embeddings = create_embeddings(
    EmbeddingSettings(provider="openai", model="text-embedding-3-small")
)
query_vector = embeddings.embed_query("Comfortable running shoes")
document_vectors = embeddings.embed_documents(["Nike running shoes", "Walking shoes"])
```

When using the OpenAI provider, the underlying LangChain implementation reads `OPENAI_API_KEY` from the environment if `api_key` is omitted.

## OpenRouter

```bash
export OPENROUTER_API_KEY="your-key"
```

```python
import os
from embedding_kit import EmbeddingSettings, create_embeddings

embeddings = create_embeddings(
    EmbeddingSettings(
        provider="openrouter",
        model="your-supported-embedding-model-id",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
)
vector = embeddings.embed_query("Running shoes")
```

Choose an embedding-capable model actually available on OpenRouter. Model identifiers and capabilities may change. OpenRouter uses its OpenAI-compatible endpoint.

## Ollama

```bash
ollama pull qwen3-embedding:0.6b
```

```python
from embedding_kit import EmbeddingSettings, create_embeddings

embeddings = create_embeddings(
    EmbeddingSettings(
        provider="ollama",
        model="qwen3-embedding:0.6b",
        base_url="http://localhost:11434",
    )
)
vector = embeddings.embed_query("Running shoes")
```

The `qwen3:8b` chat model is not the same as the dedicated `qwen3-embedding` model.

## Async / batch

```python
vectors = await embeddings.aembed_documents(["First document", "Second document"])
query_vector = await embeddings.aembed_query("Example query")
```

## Application configuration and dependency injection

Construct `EmbeddingSettings` in your application's composition root, using your own settings loader, and call `create_embeddings` once. Inject the resulting `langchain_core.embeddings.Embeddings` instance into Catalog, Knowledge, or LangChain vector stores. Business logic should not choose the provider or read credentials.

The public API is intentionally small:

- `EmbeddingSettings`: validated provider/model/options
- `create_embeddings(settings)`: returns LangChain `Embeddings`

LangChain handles embedding requests, batches and async methods. No duplicate provider interface or embedding implementation is introduced.

## Vector compatibility

Do **not** combine embeddings from different models in one semantic-search index. Record model name and vector dimension in your indexing configuration; changing models generally requires re-embedding data and rebuilding the index.

## Responsibilities

- **This package:** provider selection, configuration validation, provider initialization.
- **Catalog / Knowledge:** document preparation, content lifecycle, indexing coordination.
- **Vector store:** vector persistence, filtering, similarity search.
- **LangGraph:** orchestration and tool calls.

## Security

Never commit API keys or `.env` files. Use environment variables or your application's secrets manager. Do not log sensitive input texts or credentials.
