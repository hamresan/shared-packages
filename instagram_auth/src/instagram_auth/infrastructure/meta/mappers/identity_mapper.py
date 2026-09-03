"""Map Meta identity DTOs to domain identities."""

from instagram_auth.baseline import InstagramAccountType
from instagram_auth.domain import InstagramExternalIdentity
from instagram_auth.infrastructure.meta.dto import MetaInstagramIdentityDto


class MetaExternalIdentityMapper:
    """Translate provider account vocabulary into the domain contract."""

    def map(self, dto: MetaInstagramIdentityDto) -> InstagramExternalIdentity:
        account_type = InstagramAccountType(dto.account_type.lower())
        return InstagramExternalIdentity(
            provider_user_id=dto.user_id,
            username=dto.username,
            account_type=account_type,
        )
