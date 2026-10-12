"""Provider selection and validation, independent from application frameworks."""

from dataclasses import dataclass
from typing import Literal

EmbeddingProviderName = Literal["openai", "openrouter", "ollama"]


@dataclass(frozen=True, slots=True)
class EmbeddingSettings:
    provider: EmbeddingProviderName
    model: str
    api_key: str | None = None
    base_url: str | None = None
    timeout: float | None = None
    max_retries: int = 2
    dimensions: int | None = None

    def __post_init__(self) -> None:
        if self.provider not in ("openai", "openrouter", "ollama"):
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
        if not self.model.strip():
            raise ValueError("Embedding model must not be empty")
        if self.provider == "openrouter" and not self.api_key:
            raise ValueError("OpenRouter requires an API key")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.dimensions is not None and self.dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if self.provider == "ollama" and self.dimensions is not None:
            raise ValueError("dimensions is only supported for OpenAI-compatible providers")
