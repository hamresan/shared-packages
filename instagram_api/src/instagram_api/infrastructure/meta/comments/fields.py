"""Field parsing for Meta Instagram comment payloads."""

from collections.abc import Mapping
from typing import cast


class MetaInstagramCommentFieldParser:
    """Parses nested optional comment fields."""

    def media_id(self, value: object) -> str | None:
        """Return a media ID from a nested media object."""

        if not isinstance(value, Mapping):
            return None
        mapping = cast(Mapping[str, object], value)
        media_id = mapping.get("id")
        return media_id if isinstance(media_id, str) and media_id else None

    def author_id(self, value: object) -> str | None:
        """Return a commenter ID from a nested user object."""

        if not isinstance(value, Mapping):
            return None
        mapping = cast(Mapping[str, object], value)
        user_id = mapping.get("id")
        return user_id if isinstance(user_id, str) and user_id else None

    def parent_id(self, value: object) -> str | None:
        """Return a parent comment ID when Meta exposes one."""

        if not isinstance(value, Mapping):
            return None
        mapping = cast(Mapping[str, object], value)
        comment_id = mapping.get("id")
        return comment_id if isinstance(comment_id, str) and comment_id else None
