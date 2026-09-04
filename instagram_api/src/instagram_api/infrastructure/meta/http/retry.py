"""Safe retry policy for Meta provider calls."""

from dataclasses import dataclass

from .errors import MetaRateLimitError, MetaTransientError
from .models import MetaHttpMethod


@dataclass(frozen=True, slots=True)
class MetaRetryPolicy:
    """Determines whether and when a failed request can be retried safely."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 2.0

    def should_retry(
        self,
        *,
        method: MetaHttpMethod,
        error: Exception,
        attempt: int,
    ) -> bool:
        """Return whether another attempt is allowed."""

        if attempt >= self.max_attempts:
            return False

        if method is not MetaHttpMethod.GET:
            return False

        return isinstance(error, MetaRateLimitError | MetaTransientError)

    def delay_seconds(self, attempt: int) -> float:
        """Return a bounded exponential delay before the next attempt."""

        delay = self.base_delay_seconds * (2 ** max(attempt - 1, 0))
        return min(delay, self.max_delay_seconds)
