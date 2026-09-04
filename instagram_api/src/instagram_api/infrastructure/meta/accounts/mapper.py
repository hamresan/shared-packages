"""Mapper for Meta Instagram account profile DTOs."""

from instagram_api.domain import InstagramAccount, InstagramAccountId

from .dto import MetaInstagramAccountDto


class MetaInstagramAccountMapper:
    """Maps typed Meta account DTOs to normalized package models."""

    def to_domain(self, dto: MetaInstagramAccountDto) -> InstagramAccount:
        """Map a provider DTO to an Instagram account."""

        return InstagramAccount(
            id=InstagramAccountId(dto.id),
            username=dto.username,
            name=dto.name,
            biography=dto.biography,
            website=dto.website,
            profile_picture_url=dto.profile_picture_url,
            followers_count=dto.followers_count,
            follows_count=dto.follows_count,
            media_count=dto.media_count,
        )
