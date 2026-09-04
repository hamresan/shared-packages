"""Mapper for Meta Instagram account profile payloads."""

from collections.abc import Mapping

from instagram_api.domain import InstagramAccount, InstagramAccountId
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramAccountMapper:
    """Maps Meta account payloads to normalized package models."""

    def to_domain(self, payload: Mapping[str, object]) -> InstagramAccount:
        """Map a provider payload to an Instagram account."""

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

        return InstagramAccount(
            id=InstagramAccountId(account_id),
            username=username,
            name=self._optional_string(payload.get("name")),
            biography=self._optional_string(payload.get("biography")),
            website=self._optional_string(payload.get("website")),
            profile_picture_url=self._optional_string(payload.get("profile_picture_url")),
            followers_count=self._optional_int(payload.get("followers_count")),
            follows_count=self._optional_int(payload.get("follows_count")),
            media_count=self._optional_int(payload.get("media_count")),
        )

    @staticmethod
    def _optional_string(value: object) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _optional_int(value: object) -> int | None:
        return value if isinstance(value, int) and not isinstance(value, bool) else None
