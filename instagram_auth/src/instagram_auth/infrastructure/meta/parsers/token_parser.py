"""Parse Meta token exchange payloads."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.dto import MetaInstagramTokenDto


class MetaTokenPayloadParser:
    """Validate provider token payload structure before mapping."""

    def parse(self, payload: dict[str, object]) -> MetaInstagramTokenDto:
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")
        if not isinstance(access_token, str) or not access_token:
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        if expires_in is not None and not isinstance(expires_in, int):
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        return MetaInstagramTokenDto(access_token=access_token, expires_in=expires_in)
