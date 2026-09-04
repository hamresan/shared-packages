"""Meta provider response decoding."""

import json
from collections.abc import Mapping
from typing import Any

from .errors import (
    MetaAuthenticationError,
    MetaInvalidResponseError,
    MetaProviderError,
    MetaRateLimitError,
    MetaTransientError,
)
from .models import MetaHttpResponse


class MetaResponseDecoder:
    """Decodes Meta responses and normalizes provider errors."""

    def decode_json(self, response: MetaHttpResponse) -> Mapping[str, Any]:
        """Return decoded JSON or raise a normalized provider error."""

        payload = self._load_json(response)
        if 200 <= response.status_code < 300:
            if isinstance(payload, Mapping):
                return payload
            raise MetaInvalidResponseError(
                message="Meta response JSON must be an object.",
                status_code=response.status_code,
            )

        raise self._build_error(response.status_code, payload)

    def _load_json(self, response: MetaHttpResponse) -> object:
        try:
            return json.loads(response.body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MetaInvalidResponseError(
                message="Meta response body is not valid JSON.",
                status_code=response.status_code,
            ) from exc

    def _build_error(self, status_code: int, payload: object) -> MetaProviderError:
        error_payload: Mapping[str, Any] = {}
        if isinstance(payload, Mapping):
            raw_error = payload.get("error")
            if isinstance(raw_error, Mapping):
                error_payload = raw_error

        message = self._string_value(error_payload.get("message")) or "Meta provider request failed."
        provider_code = self._int_value(error_payload.get("code"))
        provider_subcode = self._int_value(error_payload.get("error_subcode"))
        trace_id = self._string_value(error_payload.get("fbtrace_id"))

        error_type: type[MetaProviderError]
        if status_code in {401, 403}:
            error_type = MetaAuthenticationError
        elif status_code == 429:
            error_type = MetaRateLimitError
        elif status_code >= 500:
            error_type = MetaTransientError
        else:
            error_type = MetaProviderError

        return error_type(
            message=message,
            status_code=status_code,
            provider_code=provider_code,
            provider_subcode=provider_subcode,
            trace_id=trace_id,
        )

    @staticmethod
    def _int_value(value: object) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _string_value(value: object) -> str | None:
        return value if isinstance(value, str) else None
