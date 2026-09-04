"""Parser for Meta Instagram media payloads."""

from collections.abc import Mapping, Sequence
from typing import cast

from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import MetaInstagramMediaDto


class MetaInstagramMediaPayloadParser:
    """Validates Meta media payloads and produces typed DTOs."""

    def parse_media(self, payload: Mapping[str, object]) -> MetaInstagramMediaDto:
        """Parse one Meta media object."""

        media_id = payload.get("id")
        media_type = payload.get("media_type")
        timestamp = payload.get("timestamp")

        if not isinstance(media_id, str) or not media_id:
            raise MetaInvalidResponseError(
                message="Meta media response is missing a valid id.",
                status_code=200,
            )
        if not isinstance(media_type, str) or not media_type:
            raise MetaInvalidResponseError(
                message="Meta media response is missing a valid media_type.",
                status_code=200,
            )
        if not isinstance(timestamp, str) or not timestamp:
            raise MetaInvalidResponseError(
                message="Meta media response is missing a valid timestamp.",
                status_code=200,
            )

        return MetaInstagramMediaDto(
            id=media_id,
            media_type=media_type,
            media_product_type=self._optional_string(payload.get("media_product_type")),
            timestamp=timestamp,
            caption=self._optional_string(payload.get("caption")),
            media_url=self._optional_string(payload.get("media_url")),
            thumbnail_url=self._optional_string(payload.get("thumbnail_url")),
            permalink=self._optional_string(payload.get("permalink")),
            children=self._children(payload.get("children")),
        )

    def parse_media_list(
        self,
        payload: Mapping[str, object],
    ) -> tuple[MetaInstagramMediaDto, ...]:
        """Parse a Meta media collection response."""

        data = payload.get("data")
        if not isinstance(data, Sequence) or isinstance(data, str | bytes):
            raise MetaInvalidResponseError(
                message="Meta media list response is missing a valid data collection.",
                status_code=200,
            )

        items: list[MetaInstagramMediaDto] = []
        for raw_item in data:
            if not isinstance(raw_item, Mapping):
                raise MetaInvalidResponseError(
                    message="Meta media list contains an invalid item.",
                    status_code=200,
                )
            items.append(self.parse_media(cast(Mapping[str, object], raw_item)))
        return tuple(items)

    @staticmethod
    def _optional_string(value: object) -> str | None:
        return value if isinstance(value, str) else None

    @staticmethod
    def _children(value: object) -> tuple[str, ...]:
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
