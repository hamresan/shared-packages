"""Webhook contract tests."""

from datetime import UTC, datetime

from instagram_api.domain import InstagramAccountId, InstagramWebhookEvent
from tests.fakes import FakeInstagramWebhookParser, FakeInstagramWebhookVerifier


def test_webhook_contracts_work_with_fakes_without_provider_dtos() -> None:
    event = InstagramWebhookEvent(
        event_id="event-1",
        event_type="comment_created",
        provider_account_id=InstagramAccountId("ig-account"),
        occurred_at=datetime.now(UTC),
    )
    verifier = FakeInstagramWebhookVerifier(result=True)
    parser = FakeInstagramWebhookParser(events=(event,))

    assert verifier.verify(b"payload", "signature") is True
    assert parser.parse(b"payload") == (event,)


def test_webhook_verifier_can_fail_closed() -> None:
    verifier = FakeInstagramWebhookVerifier(result=False)

    assert verifier.verify(b"payload", None) is False
