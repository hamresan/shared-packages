"""Meta provider response decoding."""

import json
from collections.abc import Mapping

from .error_decoder import MetaErrorDecoder
from .errors import MetaInvalidResponseError
from .models import MetaHttpResponse


class MetaResponseDecoder:
    """Decodes Meta responses into provider-neutral JSON objects."""

    def __init__(self, error_decoder: MetaErrorDecoder) -> None:
        self._error_decoder = error_decoder

    def decode_json(self, response: MetaHttpResponse) -> Mapping[str, object]:
        """Return decoded JSON or raise a normalized provider error."""

        try:
            payload: object = json.loads(response.body)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MetaInvalidResponseError(
                message="Meta response body is not valid JSON.",
                status_code=response.status_code,
            ) from exc

        if not 200 <= response.status_code < 300:
            raise self._error_decoder.decode(response.status_code, payload)

        if not isinstance(payload, Mapping):
            raise MetaInvalidResponseError(
                message="Meta response JSON must be an object.",
                status_code=response.status_code,
            )

        return payload
