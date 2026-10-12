"""Reusable, configuration-driven embedding providers."""

from embedding_kit.configuration import EmbeddingSettings
from embedding_kit.factories import create_embeddings

__all__ = ["EmbeddingSettings", "create_embeddings"]
