"""Field parsing helpers for Meta Instagram media payloads."""

from collections.abc import Mapping, Sequence
from typing import cast


class MetaInstagramMediaFieldParser:
    """Parses optional scalar and child-media fields."""

    def optional_string(self, value: object) -> str | None:
        """Return a string value when present and valid."""

        return value if isinstance(value, str) else None

    def child_ids(self, value: object) -> tuple[str, ...]:
        """Extract valid child media IDs from a Meta children edge."""

        if not isinstance(value, Mapping):
            return ()

        children_mapping = cast(Mapping[str, object], value)
        raw_data = children_mapping.get("data")
        if not isinstance(raw_data, Sequence) or isinstance(raw_data, str | bytes):
            return ()

        child_ids: list[str] = []
        for raw_child in raw_data:
            if not isinstance(raw_child, Mapping):
                continue
            child_mapping = cast(Mapping[str, object], raw_child)
            child_id = child_mapping.get("id")
            if isinstance(child_id, str) and child_id:
                child_ids.append(child_id)
        return tuple(child_ids)
