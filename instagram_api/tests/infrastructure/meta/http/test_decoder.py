"""Meta response and error decoder tests."""

import pytest

from instagram_api.infrastructure.meta.http import (
    MetaAuthenticationError,
    MetaErrorDecoder,
    MetaHttpResponse,
    MetaInvalidResponseError,
    MetaProviderError,
    MetaRateLimitError,
    MetaResponseDecoder,
    MetaTransientError,
)


def build_decoder() -> MetaResponseDecoder:
    return MetaResponseDecoder(MetaErrorDecoder())


def test_decoder_returns_mapping_for_success_response() -> None:
    payload = build_decoder().decode_json(
        MetaHttpResponse(
            status_code=200,
            headers={},
            body=b'{"id":"ig-account"}',
        )
    )

    assert payload == {"id": "ig-account"}


@pytest.mark.parametrize(
    ("status_code", "error_type"),
    [
        (400, MetaProviderError),
        (401, MetaAuthenticationError),
        (403, MetaAuthenticationError),
        (429, MetaRateLimitError),
        (500, MetaTransientError),
    ],
)
def test_decoder_normalizes_provider_errors(
    status_code: int,
    error_type: type[MetaProviderError],
) -> None:
    response = MetaHttpResponse(
        status_code=status_code,
        headers={},
        body=(
            b'{"error":{"message":"failure","code":10,'
            b'"error_subcode":20,"fbtrace_id":"trace"}}'
        ),
    )

    with pytest.raises(error_type) as exc_info:
        build_decoder().decode_json(response)

    error = exc_info.value
    assert error.message == "failure"
    assert error.provider_code == 10
    assert error.provider_subcode == 20
    assert error.trace_id == "trace"


def test_decoder_rejects_invalid_or_non_object_json() -> None:
    decoder = build_decoder()

    with pytest.raises(MetaInvalidResponseError):
        decoder.decode_json(MetaHttpResponse(200, {}, b"not-json"))

    with pytest.raises(MetaInvalidResponseError):
        decoder.decode_json(MetaHttpResponse(200, {}, b"[]"))
