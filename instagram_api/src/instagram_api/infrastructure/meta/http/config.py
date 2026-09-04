"""Meta API and timeout configuration."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaApiConfig:
    """Configuration used to build versioned Meta API requests."""

    api_version: str
    base_url: str = "https://graph.instagram.com"

    def build_url(self, path: str) -> str:
        """Build a versioned absolute API URL."""

        normalized_path = path.lstrip("/")
        return f"{self.base_url.rstrip('/')}/{self.api_version}/{normalized_path}"


@dataclass(frozen=True, slots=True)
class MetaTimeoutConfig:
    """Bounded timeout configuration for Meta HTTP calls."""

    connect_seconds: float = 5.0
    read_seconds: float = 15.0
    write_seconds: float = 15.0
    pool_seconds: float = 5.0
