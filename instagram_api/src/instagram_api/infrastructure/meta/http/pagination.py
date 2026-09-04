"""Meta pagination mapping."""

from collections.abc import Mapping
from typing import cast

from instagram_api.domain import PaginationCursor


class MetaPaginationCursorMapper:
    """Extracts package-owned pagination cursors from Meta paging payloads."""

    def next_cursor(self, payload: Mapping[str, object]) -> PaginationCursor | None:
        """Return the next cursor when Meta exposes one."""

        paging = payload.get("paging")
        if not isinstance(paging, Mapping):
            return None

        paging_mapping = cast(Mapping[str, object], paging)
        cursors = paging_mapping.get("cursors")
        if not isinstance(cursors, Mapping):
            return None

        cursors_mapping = cast(Mapping[str, object], cursors)
        after = cursors_mapping.get("after")
        if not isinstance(after, str) or not after:
            return None

        return PaginationCursor(after)
