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
        if not isinstance(user_id, str) or not user_id:
            raise self.invalid_payload_error()
        if not isinstance(username, str) or not username:
            raise self.invalid_payload_error()
        if not isinstance(account_type, str) or not account_type:
            raise self.invalid_payload_error()
        return MetaInstagramIdentityDto(
            user_id=user_id,
            username=username,
            account_type=account_type,
        )

    @staticmethod
    def invalid_payload_error() -> InstagramProviderError:
        return InstagramProviderError(
            kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
            message="Instagram provider error: unexpected_provider_error",
        )
