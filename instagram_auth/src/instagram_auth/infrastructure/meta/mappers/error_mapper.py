"""Normalize Meta failures into application-safe provider errors."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.http import MetaHttpResponse


class MetaProviderErrorMapper:
    """Map endpoint-aware provider failures without exposing provider payloads."""

    def token_exchange_error(self, response: MetaHttpResponse) -> InstagramProviderError:
        if response.status_code == 429:
            return self._error(InstagramProviderErrorKind.RATE_LIMITED, response.status_code)
        if response.status_code >= 500:
            return self._error(InstagramProviderErrorKind.PROVIDER_UNAVAILABLE, response.status_code)
        if response.status_code == 400:
            return self._error(InstagramProviderErrorKind.INVALID_AUTHORIZATION_CODE, 400)
        return self._error(InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR, response.status_code)

    def identity_error(self, response: MetaHttpResponse) -> InstagramProviderError:
        if response.status_code == 429:
            return self._error(InstagramProviderErrorKind.RATE_LIMITED, response.status_code)
        if response.status_code >= 500:
            return self._error(InstagramProviderErrorKind.PROVIDER_UNAVAILABLE, response.status_code)
        if response.status_code in {400, 401}:
            return self._error(InstagramProviderErrorKind.INVALID_TOKEN, response.status_code)
        return self._error(InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR, response.status_code)

    def timeout_error(self) -> InstagramProviderError:
        return self._error(InstagramProviderErrorKind.TIMEOUT, None)

    def transport_error(self) -> InstagramProviderError:
        return self._error(InstagramProviderErrorKind.PROVIDER_UNAVAILABLE, None)

    @staticmethod
    def _error(kind: InstagramProviderErrorKind, status_code: int | None) -> InstagramProviderError:
        return InstagramProviderError(kind=kind, message=f"Instagram provider error: {kind.value}", status_code=status_code)
