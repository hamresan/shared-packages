from datetime import timedelta
from uuid import uuid4

import pytest

from identity.application.dto import RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import (
    IdentityRateLimitExceededError,
    OtpChallengeNotFoundError,
)
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


@pytest.mark.asyncio
async def test_equivalent_email_forms_share_request_rate_limit_bucket() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(
        database,
        sender,
        otp_resend_delay=timedelta(0),
        otp_request_burst_limit=2,
    )

    try:
        await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination=" User@Example.com ",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="user@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )

        with pytest.raises(IdentityRateLimitExceededError):
            await module.otp_requester.execute(
                RequestOtpCommand(
                    identity_type=IdentityType.EMAIL,
                    destination="USER@EXAMPLE.COM",
                    purpose=OtpPurpose.REGISTRATION,
                )
            )
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_cooldown_reuse_does_not_consume_destination_send_quota() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(
        database,
        sender,
        otp_request_burst_limit=1,
    )
    command = RequestOtpCommand(
        identity_type=IdentityType.EMAIL,
        destination="cooldown-quota@example.com",
        purpose=OtpPurpose.REGISTRATION,
    )

    try:
        first = await module.otp_requester.execute(command)
        second = await module.otp_requester.execute(command)
        third = await module.otp_requester.execute(command)

        assert second.challenge_id == first.challenge_id
        assert third.challenge_id == first.challenge_id
        assert len(sender.commands) == 1
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_verify_requester_limit_applies_across_unknown_challenge_ids() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(
        database,
        sender,
        otp_verify_requester_burst_limit=2,
    )
    requester_ip = "203.0.113.45"

    try:
        for _ in range(2):
            with pytest.raises(OtpChallengeNotFoundError):
                await module.otp_verifier.execute(
                    VerifyOtpCommand(
                        challenge_id=uuid4(),
                        code="000000",
                        ip_address=requester_ip,
                    )
                )

        with pytest.raises(IdentityRateLimitExceededError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=uuid4(),
                    code="000000",
                    ip_address=requester_ip,
                )
            )
    finally:
        await database.close()
