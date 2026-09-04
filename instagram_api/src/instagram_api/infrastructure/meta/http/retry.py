"""Safe retry policy for Meta provider calls."""

from dataclasses import dataclass

from .errors import MetaRateLimitError, MetaTransientError
from .models import MetaHttpMethod


@dataclass(frozen=True, slots=True)
class MetaRetryPolicy:
    """Determines whether a failed request can be retried safely."""

    max_attempts: int = 3

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
