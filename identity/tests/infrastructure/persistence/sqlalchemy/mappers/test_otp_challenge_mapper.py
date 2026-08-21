from datetime import UTC, datetime, timedelta

from identity.application.factories.entities import OtpChallengeFactory
from identity.domain import IdentityType, OtpPurpose
from identity.infrastructure.persistence.sqlalchemy.mappers import OtpChallengeMapper


def test_otp_challenge_mapper_round_trip() -> None:
    now = datetime(2026, 8, 21, 8, 0, tzinfo=UTC)
    challenge = OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=5,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=OtpPurpose.LOGIN,
        code_hash="otp-hash",
        user_id=None,
        identity_id=None,
    )

    mapper = OtpChallengeMapper()
    mapped = mapper.to_domain(mapper.to_model(challenge))

    assert mapped == challenge
