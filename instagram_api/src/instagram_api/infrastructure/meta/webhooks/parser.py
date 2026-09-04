"""Generic Meta Instagram webhook envelope parser."""

import json

from instagram_api.application.contracts.webhooks import InstagramWebhookParser
from instagram_api.domain import InstagramWebhookEvent
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .fields import MetaInstagramWebhookFieldParser
from .mapper import MetaInstagramWebhookEventMapper
from .messaging_mapper import MetaInstagramMessagingWebhookMapper


class MetaInstagramWebhookParser(InstagramWebhookParser):
    """Parses generic envelopes and normalizes supported messaging payloads."""

    def __init__(
        self,
        field_parser: MetaInstagramWebhookFieldParser,
        event_mapper: MetaInstagramWebhookEventMapper,
        messaging_mapper: MetaInstagramMessagingWebhookMapper,
    ) -> None:
        self._field_parser = field_parser
        self._event_mapper = event_mapper
        self._messaging_mapper = messaging_mapper

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

            changes = entry.get("changes")
            if changes is not None:
                for raw_change in self._field_parser.sequence(changes, "changes"):
                    change = self._field_parser.mapping(raw_change, "change")
                    field = self._field_parser.required_string(
                        change.get("field"),
                        "change field",
                    )
                    events.append(
                        self._event_mapper.to_domain(
                            account_id=account_id,
                            event_type=f"change:{field}",
                            occurred_at_seconds=occurred_seconds,
                            item=change,
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
