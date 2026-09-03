"""Retry policy for idempotent Meta identity reads."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaIdentityRetryPolicy:
    """Limit retries to transient failures on safe identity GET requests."""

    max_attempts: int = 2

    def should_retry_status(self, *, status_code: int, attempt: int) -> bool:
        return status_code >= 500 and attempt < self.max_attempts

    def should_retry_transport(self, *, attempt: int) -> bool:
        return attempt < self.max_attempts
