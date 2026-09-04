"""Normalized Meta provider HTTP errors."""

from dataclasses import dataclass


@dataclass(eq=False)
class MetaProviderError(Exception):
    """Base normalized provider error."""

    message: str
    status_code: int
    provider_code: int | None = None
    provider_subcode: int | None = None
    trace_id: str | None = None

    def __str__(self) -> str:
        return self.message


class MetaAuthenticationError(MetaProviderError):
    """Provider authentication or authorization failure."""


class MetaRateLimitError(MetaProviderError):
    """Provider rate-limit failure."""


class MetaTransientError(MetaProviderError):
    """Provider failure that may be retried for an idempotent operation."""


class MetaTimeoutError(MetaTransientError):
    """Provider transport timed out before a response was completed."""


class MetaInvalidResponseError(MetaProviderError):
    """Provider response could not be decoded safely."""
