from unittest.mock import MagicMock, patch

from embedding_kit import EmbeddingSettings, create_embeddings


def test_openrouter_uses_openai_compatible_endpoint() -> None:
    with patch("langchain_openai.OpenAIEmbeddings") as provider:
        provider.return_value = MagicMock()
        create_embeddings(
            EmbeddingSettings(
                provider="openrouter",
                model="provider/embedding-model",
                api_key="test-key",
            )
        )

    kwargs = provider.call_args.kwargs
    assert kwargs["base_url"] == "https://openrouter.ai/api/v1"
    assert kwargs["check_embedding_ctx_length"] is False


def test_ollama_uses_local_model() -> None:
    with patch("langchain_ollama.OllamaEmbeddings") as provider:
        provider.return_value = MagicMock()
        create_embeddings(
            EmbeddingSettings(provider="ollama", model="qwen3-embedding:0.6b")
        )

    assert provider.call_args.kwargs["model"] == "qwen3-embedding:0.6b"
