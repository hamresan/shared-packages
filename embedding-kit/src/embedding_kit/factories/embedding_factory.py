"""Build LangChain Embeddings objects from explicit settings."""

from langchain_core.embeddings import Embeddings

from embedding_kit.configuration import EmbeddingSettings


def create_embeddings(settings: EmbeddingSettings) -> Embeddings:
    """Create an embedding implementation without exposing provider selection to callers."""
    if settings.provider in ("openai", "openrouter"):
        from langchain_openai import OpenAIEmbeddings

        api_key = settings.api_key
        if settings.provider == "openrouter":
            base_url = settings.base_url or "https://openrouter.ai/api/v1"
        else:
            base_url = settings.base_url

        options: dict[str, object] = {
            "model": settings.model,
            "max_retries": settings.max_retries,
        }
        if api_key:
            options["api_key"] = api_key
        if base_url:
            options["base_url"] = base_url
        if settings.timeout is not None:
            options["request_timeout"] = settings.timeout
        if settings.dimensions is not None:
            options["dimensions"] = settings.dimensions
        if settings.provider == "openrouter":
            options["check_embedding_ctx_length"] = False

        return OpenAIEmbeddings(**options)  # type: ignore[arg-type]

    if settings.provider == "ollama":
        from langchain_ollama import OllamaEmbeddings

        options = {"model": settings.model}
        if settings.base_url:
            options["base_url"] = settings.base_url
        if settings.timeout is not None:
            options["client_kwargs"] = {"timeout": settings.timeout}
        return OllamaEmbeddings(**options)  # type: ignore[arg-type]

    raise ValueError(f"Unsupported embedding provider: {settings.provider}")
