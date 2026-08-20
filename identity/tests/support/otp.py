from datetime import UTC, datetime, timedelta
from uuid import UUID

from identity.application.factories.entities import OtpChallengeFactory
from identity.domain import IdentityType, OtpChallenge, OtpPurpose
from tests.support.integrations import FakeNotificationSender


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    if not isinstance(value, str):
        raise AssertionError("Expected OTP notification variable to be a string")
    return value


def invalid_otp_for(valid_otp: str) -> str:
    return "111111" if valid_otp == "000000" else "000000"


def build_otp_challenge(
    *,
    purpose: OtpPurpose,
    user_id: UUID | None = None,
    now: datetime | None = None,
    code_hash: str = "hash",
    identity_type: IdentityType = IdentityType.EMAIL,
    destination: str = "user@example.com",
) -> OtpChallenge:
    created_at = now or datetime.now(UTC)
    return OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=5,
    ).create(
        now=created_at,
        identity_type=identity_type,
        destination=destination,
        purpose=purpose,
        code_hash=code_hash,
        user_id=user_id,
        identity_id=None,
    )
