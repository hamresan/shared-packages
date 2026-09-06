"""Generic Meta Instagram webhook envelope parser."""

import json

from instagram_api.application.contracts.webhooks import InstagramWebhookParser
from instagram_api.domain import InstagramWebhookEvent, InstagramWebhookPayload
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .comment_mapper import MetaInstagramCommentWebhookMapper
from .comment_parser import MetaInstagramCommentWebhookPayloadParser
from .fields import MetaInstagramWebhookFieldParser
from .mapper import MetaInstagramWebhookEventMapper
from .messaging_mapper import MetaInstagramMessagingWebhookMapper


class MetaInstagramWebhookParser(InstagramWebhookParser):
    """Parses generic envelopes and normalizes supported webhook payloads."""

    _COMMENT_FIELDS = {"comments", "live_comments"}

    def __init__(
        self,
        field_parser: MetaInstagramWebhookFieldParser,
        event_mapper: MetaInstagramWebhookEventMapper,
        messaging_mapper: MetaInstagramMessagingWebhookMapper,
        comment_parser: MetaInstagramCommentWebhookPayloadParser,
        comment_mapper: MetaInstagramCommentWebhookMapper,
    ) -> None:
        self._field_parser = field_parser
        self._event_mapper = event_mapper
        self._messaging_mapper = messaging_mapper
        self._comment_parser = comment_parser
        self._comment_mapper = comment_mapper

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        """Return normalized events from a Meta Instagram envelope."""

        try:
            decoded: object = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise MetaInvalidResponseError(
                message="Meta webhook payload is not valid JSON.",
                status_code=200,
            ) from exc

        root = self._field_parser.mapping(decoded, "root")
        entries = self._field_parser.sequence(root.get("entry"), "entry")
        events: list[InstagramWebhookEvent] = []

        for raw_entry in entries:
            entry = self._field_parser.mapping(raw_entry, "entry")
            account_id = self._field_parser.required_string(
                entry.get("id"),
                "provider account id",
            )
            occurred_seconds = self._field_parser.optional_int(entry.get("time"))

            direct_field = entry.get("field")
            direct_value = entry.get("value")
            if (
                isinstance(direct_field, str)
                and direct_field in self._COMMENT_FIELDS
                and direct_value is not None
            ):
                value = self._field_parser.mapping(direct_value, "comment value")
                dto = self._comment_parser.parse(
                    field=direct_field,
                    value=value,
                )
                normalized_payload = self._comment_mapper.created(dto)
                direct_item: dict[str, object] = {
                    "field": direct_field,
                    "value": value,
                }
                events.append(
                    self._event_mapper.to_domain(
                        account_id=account_id,
                        event_type="comment:created",
                        occurred_at_seconds=occurred_seconds,
                        item=direct_item,
                        payload=normalized_payload,
                    )
                )

            changes = entry.get("changes")
            if changes is not None:
                for raw_change in self._field_parser.sequence(changes, "changes"):
                    change = self._field_parser.mapping(raw_change, "change")
                    field = self._field_parser.required_string(
                        change.get("field"),
                        "change field",
                    )
                    normalized_payload: InstagramWebhookPayload | None = None
                    event_type = f"change:{field}"

                    if field in self._COMMENT_FIELDS:
                        raw_value = change.get("value")
                        value = self._field_parser.mapping(
                            raw_value,
                            "comment change value",
                        )
                        dto = self._comment_parser.parse(
                            field=field,
                            value=value,
                        )
                        normalized_payload = self._comment_mapper.created(dto)
                        event_type = "comment:created"

                    events.append(
                        self._event_mapper.to_domain(
                            account_id=account_id,
                            event_type=event_type,
                            occurred_at_seconds=occurred_seconds,
                            item=change,
                            payload=normalized_payload,
                        )
                    )

            messaging = entry.get("messaging")
            if messaging is not None:
                for raw_message in self._field_parser.sequence(
                    messaging,
                    "messaging",
                ):
                    message = self._field_parser.mapping(raw_message, "messaging item")
                    normalized_payload = self._messaging_mapper.to_domain(message)
                    events.append(
                        self._event_mapper.to_domain(
                            account_id=account_id,
                            event_type="messaging",
                            occurred_at_seconds=occurred_seconds,
                            item=message,
                            payload=normalized_payload,
                        )
                    )

        return tuple(events)
