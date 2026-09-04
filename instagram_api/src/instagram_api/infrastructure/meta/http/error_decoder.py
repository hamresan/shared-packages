"""Meta provider error decoding."""

from collections.abc import Mapping
from typing import cast

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

        error_payload: Mapping[str, object] = {}
        if isinstance(payload, Mapping):
            payload_mapping = cast(Mapping[str, object], payload)
            raw_error = payload_mapping.get("error")
            if isinstance(raw_error, Mapping):
                error_payload = cast(Mapping[str, object], raw_error)

        raw_message = error_payload.get("message")
        message = raw_message if isinstance(raw_message, str) else "Meta provider request failed."

        raw_code = error_payload.get("code")
        provider_code = raw_code if isinstance(raw_code, int) else None

        raw_subcode = error_payload.get("error_subcode")
        provider_subcode = raw_subcode if isinstance(raw_subcode, int) else None

        raw_trace_id = error_payload.get("fbtrace_id")
        trace_id = raw_trace_id if isinstance(raw_trace_id, str) else None

        error_type: type[MetaProviderError] = MetaProviderError
        if status_code in {401, 403}:
            error_type = MetaAuthenticationError
        elif status_code == 429:
            error_type = MetaRateLimitError
        elif status_code >= 500:
            error_type = MetaTransientError

        return error_type(
            message=message,
            status_code=status_code,
            provider_code=provider_code,
            provider_subcode=provider_subcode,
            trace_id=trace_id,
        )
