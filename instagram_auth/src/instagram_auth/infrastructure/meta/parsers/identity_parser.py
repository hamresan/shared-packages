"""Parse Meta identity payloads."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind
from instagram_auth.infrastructure.meta.dto import MetaInstagramIdentityDto


class MetaIdentityPayloadParser:
    """Validate provider identity payload structure before domain mapping."""

    def parse(self, payload: dict[str, object]) -> MetaInstagramIdentityDto:
        user_id = payload.get("user_id")
        username = payload.get("username")
        account_type = payload.get("account_type")
        values = (user_id, username, account_type)
        if not all(isinstance(value, str) and value for value in values):
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        return MetaInstagramIdentityDto(
            user_id=user_id,
            username=username,
            account_type=account_type,
        )
