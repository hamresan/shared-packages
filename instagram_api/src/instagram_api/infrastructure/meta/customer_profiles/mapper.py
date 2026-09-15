"""Mapper from Meta customer profile DTOs to domain models."""

from instagram_api.domain import InstagramCustomerProfile, InstagramUserId

from .dto import MetaInstagramCustomerProfileDto


class MetaInstagramCustomerProfileMapper:
    """Maps provider customer profile DTOs into provider-neutral domain models."""

    def to_domain(self, dto: MetaInstagramCustomerProfileDto) -> InstagramCustomerProfile:
        """Return the normalized Instagram customer profile."""

        return InstagramCustomerProfile(
            id=InstagramUserId(dto.user_id),
            username=dto.username,
            name=dto.name,
            profile_picture_url=dto.profile_picture_url,
        )
