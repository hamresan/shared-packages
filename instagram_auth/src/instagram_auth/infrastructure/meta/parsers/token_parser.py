"""Parse Meta token exchange payloads."""

from collections.abc import Iterable

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.dto import MetaInstagramTokenDto


class MetaTokenPayloadParser:
    """Validate provider token payload structure before mapping."""

    def parse(self, payload: dict[str, object]) -> MetaInstagramTokenDto:
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")
        permissions = payload.get("permissions")
        if not isinstance(access_token, str) or not access_token:
            raise self._unexpected_payload()
        if expires_in is not None and not isinstance(expires_in, int):
            raise self._unexpected_payload()
        return MetaInstagramTokenDto(
            access_token=access_token,
            expires_in=expires_in,
            permissions=self._parse_permissions(permissions),
        )

    def _parse_permissions(self, value: object) -> frozenset[str]:
        if value is None:
            return frozenset()
        if isinstance(value, str):
            return frozenset(item.strip() for item in value.split(",") if item.strip())
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
            items = tuple(value)
            if all(isinstance(item, str) and item for item in items):
                return frozenset(items)
        raise self._unexpected_payload()

    def _unexpected_payload(self) -> InstagramProviderError:
        return InstagramProviderError(
            kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
            message="Instagram provider error: unexpected_provider_error",
        )
