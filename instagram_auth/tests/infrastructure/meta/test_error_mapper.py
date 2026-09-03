import pytest

from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.http import MetaHttpResponse
from instagram_auth.infrastructure.meta.mappers import MetaProviderErrorMapper


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (429, InstagramProviderErrorKind.RATE_LIMITED),
        (500, InstagramProviderErrorKind.PROVIDER_UNAVAILABLE),
        (400, InstagramProviderErrorKind.INVALID_AUTHORIZATION_CODE),
        (403, InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR),
    ],
)
def test_token_error_mapping(status_code: int, expected: InstagramProviderErrorKind) -> None:
    error = MetaProviderErrorMapper().token_exchange_error(MetaHttpResponse(status_code, {}))
    assert error.kind is expected


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (429, InstagramProviderErrorKind.RATE_LIMITED),
        (503, InstagramProviderErrorKind.PROVIDER_UNAVAILABLE),
        (400, InstagramProviderErrorKind.INVALID_TOKEN),
        (401, InstagramProviderErrorKind.INVALID_TOKEN),
        (403, InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR),
    ],
)
def test_identity_error_mapping(status_code: int, expected: InstagramProviderErrorKind) -> None:
    error = MetaProviderErrorMapper().identity_error(MetaHttpResponse(status_code, {}))
    assert error.kind is expected
