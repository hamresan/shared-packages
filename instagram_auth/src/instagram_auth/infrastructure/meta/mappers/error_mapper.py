"""Normalize Meta failures into application-safe provider errors."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.http import MetaHttpResponse


class MetaProviderErrorMapper:
    """Map endpoint-aware provider failures without exposing provider payloads."""

    def token_exchange_error(self, response: MetaHttpResponse) -> InstagramProviderError:
        if response.status_code == 429:
            kind = InstagramProviderErrorKind.RATE_LIMITED
        elif response.status_code >= 500:
            kind = InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
        elif response.status_code == 400:
            kind = InstagramProviderErrorKind.INVALID_AUTHORIZATION_CODE
        else:
            kind = InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR
        return InstagramProviderError(
            kind=kind,
            message=f"Instagram provider error: {kind.value}",
            status_code=response.status_code,
        )

    def token_refresh_error(self, response: MetaHttpResponse) -> InstagramProviderError:
        if response.status_code == 429:
            kind = InstagramProviderErrorKind.RATE_LIMITED
        elif response.status_code >= 500:
            kind = InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
        elif response.status_code in {400, 401}:
            kind = InstagramProviderErrorKind.INVALID_TOKEN
        else:
            kind = InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR
        return InstagramProviderError(
            kind=kind,
            message=f"Instagram provider error: {kind.value}",
            status_code=response.status_code,
        )

    def identity_error(self, response: MetaHttpResponse) -> InstagramProviderError:
        if response.status_code == 429:
            kind = InstagramProviderErrorKind.RATE_LIMITED
        elif response.status_code >= 500:
            kind = InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
        elif response.status_code in {400, 401}:
            kind = InstagramProviderErrorKind.INVALID_TOKEN
        else:
            kind = InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR
        return InstagramProviderError(
            kind=kind,
            message=f"Instagram provider error: {kind.value}",
            status_code=response.status_code,
        )

    def timeout_error(self) -> InstagramProviderError:
        kind = InstagramProviderErrorKind.TIMEOUT
        return InstagramProviderError(kind=kind, message=f"Instagram provider error: {kind.value}")

    def transport_error(self) -> InstagramProviderError:
        kind = InstagramProviderErrorKind.PROVIDER_UNAVAILABLE
        return InstagramProviderError(kind=kind, message=f"Instagram provider error: {kind.value}")
