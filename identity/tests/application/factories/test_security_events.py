from datetime import UTC, datetime
from uuid import uuid4

from identity.application.contracts.security_events import SecurityEventName
from identity.application.factories.security_events import IdentitySecurityEventFactory
from identity.domain import OtpPurpose
from tests.support.access_tokens import build_session
from tests.support.hmac import build_hmac_hasher
from tests.support.otp import build_otp_challenge

TEST_SECRET = b"security-event-factory-test-key!"


def test_factory_builds_otp_request_rate_limited_event_with_fingerprint() -> None:
    now = datetime.now(UTC)
    hasher = build_hmac_hasher(TEST_SECRET)
    factory = IdentitySecurityEventFactory(hasher)

    event = factory.otp_request_rate_limited(
        occurred_at=now,
        destination="user@example.com",
    )

    assert event.name is SecurityEventName.OTP_REQUEST_RATE_LIMITED
    assert event.occurred_at == now
    assert event.subject_fingerprint == hasher.hash("user@example.com")


def test_factory_builds_otp_verification_events_from_challenge() -> None:
    now = datetime.now(UTC)
    user_id = uuid4()
    challenge = build_otp_challenge(
        purpose=OtpPurpose.LOGIN,
        user_id=user_id,
        now=now,
    )
    factory = IdentitySecurityEventFactory(build_hmac_hasher(TEST_SECRET))

    rate_limited = factory.otp_verify_rate_limited(
        occurred_at=now,
        challenge_id=challenge.id,
    )
    failed = factory.otp_attempt_failed(occurred_at=now, challenge=challenge)
    exceeded = factory.otp_attempts_exceeded(occurred_at=now, challenge=challenge)

    assert rate_limited.name is SecurityEventName.OTP_VERIFY_RATE_LIMITED
    assert rate_limited.challenge_id == challenge.id
    assert failed.name is SecurityEventName.OTP_ATTEMPT_FAILED
    assert failed.user_id == user_id
    assert failed.challenge_id == challenge.id
    assert exceeded.name is SecurityEventName.OTP_ATTEMPTS_EXCEEDED
    assert exceeded.user_id == user_id
    assert exceeded.challenge_id == challenge.id


def test_factory_builds_session_security_events() -> None:
    now = datetime.now(UTC)
    user_id = uuid4()
    session = build_session(
        user_id=user_id,
        session_id=uuid4(),
        now=now,
    )
    factory = IdentitySecurityEventFactory(build_hmac_hasher(TEST_SECRET))

    reuse = factory.refresh_reuse_detected(occurred_at=now, session=session)
    revoked = factory.session_revoked(occurred_at=now, session=session)
    revoked_all = factory.sessions_revoked_all(occurred_at=now, user_id=user_id)

    assert reuse.name is SecurityEventName.REFRESH_REUSE_DETECTED
    assert reuse.user_id == user_id
    assert reuse.session_id == session.id
    assert reuse.family_id == session.family_id
    assert revoked.name is SecurityEventName.SESSION_REVOKED
    assert revoked.user_id == user_id
    assert revoked.session_id == session.id
    assert revoked.family_id == session.family_id
    assert revoked_all.name is SecurityEventName.SESSIONS_REVOKED_ALL
    assert revoked_all.user_id == user_id
