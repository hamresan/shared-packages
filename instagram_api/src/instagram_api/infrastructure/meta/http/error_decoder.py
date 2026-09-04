"""Meta provider error decoding."""

from collections.abc import Mapping
from typing import Any

from .errors import (
    MetaAuthenticationError,
    MetaProviderError,
    MetaRateLimitError,
    MetaTransientError,
)


class MetaErrorDecoder:
    """Maps Meta error payloads to normalized provider exceptions."""

    def decode(self, status_code: int, payload: object) -> MetaProviderError:
        """Build a normalized error from a provider response payload."""

        error_payload = self._error_payload(payload)
        message = self._string_value(error_payload.get("message")) or "Meta provider request failed."
        provider_code = self._int_value(error_payload.get("code"))
        provider_subcode = self._int_value(error_payload.get("error_subcode"))
        trace_id = self._string_value(error_payload.get("fbtrace_id"))
        error_type = self._error_type(status_code)

        return error_type(
            message=message,
            status_code=status_code,
            provider_code=provider_code,
            provider_subcode=provider_subcode,
            trace_id=trace_id,
        )

    @staticmethod
    def _error_payload(payload: object) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            return {}

        raw_error = payload.get("error")
        return raw_error if isinstance(raw_error, Mapping) else {}

    @staticmethod
    def _error_type(status_code: int) -> type[MetaProviderError]:
        if status_code in {401, 403}:
            return MetaAuthenticationError
        if status_code == 429:
            return MetaRateLimitError
        if status_code >= 500:
            return MetaTransientError
        return MetaProviderError

    @staticmethod
    def _int_value(value: object) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _string_value(value: object) -> str | None:
        return value if isinstance(value, str) else None
