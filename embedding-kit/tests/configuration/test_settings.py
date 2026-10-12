import pytest

from embedding_kit import EmbeddingSettings


def test_openrouter_requires_api_key() -> None:
    with pytest.raises(ValueError, match="API key"):
        EmbeddingSettings(provider="openrouter", model="example")


def test_model_is_required() -> None:
    with pytest.raises(ValueError, match="model"):
        EmbeddingSettings(provider="openai", model=" ")


def test_ollama_rejects_dimensions() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        EmbeddingSettings(provider="ollama", model="qwen3-embedding:0.6b", dimensions=512)
