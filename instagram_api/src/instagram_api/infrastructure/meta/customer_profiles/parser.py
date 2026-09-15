"""Parser for Meta Instagram customer profile payloads."""

from collections.abc import Mapping

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import MetaInstagramCustomerProfileDto


class MetaInstagramCustomerProfilePayloadParser:
    """Validates and parses Meta customer profile payloads into a typed DTO."""

    def parse(self, payload: Mapping[str, object]) -> MetaInstagramCustomerProfileDto:
        """Parse a provider payload and reject an invalid required user ID."""

        user_id = payload.get("id")
        if not isinstance(user_id, str) or not user_id:
            raise MetaInvalidResponseError(
                message="Meta customer profile response is missing a valid id.",
                status_code=200,
            )

        username = payload.get("username")
        name = payload.get("name")
        profile_picture_url = payload.get("profile_pic")

        return MetaInstagramCustomerProfileDto(
            user_id=user_id,
            username=username if isinstance(username, str) and username else None,
            name=name if isinstance(name, str) and name else None,
            profile_picture_url=(
                profile_picture_url
                if isinstance(profile_picture_url, str) and profile_picture_url
                else None
            ),
        )
