"""Map Meta identity DTOs to domain identities."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramAccountType, InstagramProviderErrorKind
from instagram_auth.domain import InstagramExternalIdentity
from instagram_auth.infrastructure.meta.dto import MetaInstagramIdentityDto


class MetaExternalIdentityMapper:
    """Translate provider account vocabulary into the domain contract."""

    def map(self, dto: MetaInstagramIdentityDto) -> InstagramExternalIdentity:
        try:
            account_type = InstagramAccountType(dto.account_type.lower())
        except ValueError as exc:
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            ) from exc
        return InstagramExternalIdentity(
            provider_user_id=dto.user_id,
            username=dto.username,
            account_type=account_type,
        )
