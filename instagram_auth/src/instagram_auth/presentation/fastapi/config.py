"""Host configuration consumed by the optional FastAPI adapter."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InstagramFastApiConfig:
    """Transport configuration owned by the host application."""

    redirect_uri: str
