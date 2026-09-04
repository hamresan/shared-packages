"""Generic Meta Instagram webhook envelope parser."""

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

from instagram_api.application.contracts.webhooks import InstagramWebhookParser
from instagram_api.domain import InstagramAccountId, InstagramWebhookEvent
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .event_id import MetaInstagramWebhookEventIdFactory
from .fields import MetaInstagramWebhookFieldParser


class MetaInstagramWebhookParser(InstagramWebhookParser):
    """Parses Meta envelopes without interpreting Stage 10+ event semantics."""

    def __init__(
        self,
        field_parser: MetaInstagramWebhookFieldParser,
        event_id_factory: MetaInstagramWebhookEventIdFactory,
    ) -> None:
        self._field_parser = field_parser
        self._event_id_factory = event_id_factory

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        """Return generic normalized events from a Meta Instagram envelope."""

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
            occurred_at = (
                datetime.fromtimestamp(occurred_seconds, tz=UTC)
                if occurred_seconds is not None
                else None
            )

            changes = entry.get("changes")
            if changes is not None:
                for raw_change in self._field_parser.sequence(changes, "changes"):
                    change = self._field_parser.mapping(raw_change, "change")
                    field = self._field_parser.required_string(
                        change.get("field"),
                        "change field",
                    )
                    events.append(
                        self._event(
                            account_id=account_id,
                            event_type=f"change:{field}",
                            occurred_seconds=occurred_seconds,
                            occurred_at=occurred_at,
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
                    events.append(
                        self._event(
                            account_id=account_id,
                            event_type="messaging",
                            occurred_seconds=occurred_seconds,
                            occurred_at=occurred_at,
                            item=message,
                        )
                    )

        return tuple(events)

    def _event(
        self,
        *,
        account_id: str,
        event_type: str,
        occurred_seconds: int | None,
        occurred_at: datetime | None,
        item: Mapping[str, object],
    ) -> InstagramWebhookEvent:
        event_id = self._event_id_factory.create(
            provider_account_id=account_id,
            event_type=event_type,
            occurred_at_seconds=occurred_seconds,
            item=cast(Mapping[str, object], item),
        )
        return InstagramWebhookEvent(
            event_id=event_id,
            event_type=event_type,
            provider_account_id=InstagramAccountId(account_id),
            occurred_at=occurred_at,
        )
