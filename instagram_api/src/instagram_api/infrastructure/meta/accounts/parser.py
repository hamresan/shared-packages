"""Parser for Meta Instagram account profile payloads."""

from collections.abc import Mapping

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import MetaInstagramAccountDto


class MetaInstagramAccountPayloadParser:
    """Validates and parses Meta account payloads into a typed DTO."""

    def parse(self, payload: Mapping[str, object]) -> MetaInstagramAccountDto:
        """Parse a provider payload and reject invalid required fields."""

        account_id = payload.get("id")
        username = payload.get("username")
        if not isinstance(account_id, str) or not account_id:
            raise MetaInvalidResponseError(
                message="Meta account response is missing a valid id.",
                status_code=200,
            )
        if not isinstance(username, str) or not username:
            raise MetaInvalidResponseError(
                message="Meta account response is missing a valid username.",
                status_code=200,
            )

        name = payload.get("name")
        biography = payload.get("biography")
        website = payload.get("website")
        profile_picture_url = payload.get("profile_picture_url")
        followers_count = payload.get("followers_count")
        follows_count = payload.get("follows_count")
        media_count = payload.get("media_count")

        return MetaInstagramAccountDto(
            id=account_id,
            username=username,
            name=name if isinstance(name, str) else None,
            biography=biography if isinstance(biography, str) else None,
            website=website if isinstance(website, str) else None,
            profile_picture_url=(
                profile_picture_url if isinstance(profile_picture_url, str) else None
            ),
            followers_count=(
                followers_count
                if isinstance(followers_count, int) and not isinstance(followers_count, bool)
                else None
            ),
            follows_count=(
                follows_count
                if isinstance(follows_count, int) and not isinstance(follows_count, bool)
                else None
            ),
            media_count=(
                media_count
                if isinstance(media_count, int) and not isinstance(media_count, bool)
                else None
            ),
        )
