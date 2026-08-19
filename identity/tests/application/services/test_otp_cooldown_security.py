import pytest

from identity.application.dto import RequestOtpCommand, VerifyOtpCommand
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    assert isinstance(value, str)
    return value


async def register_user(
    *,
    module: object,
    sender: FakeNotificationSender,
    destination: str,
) -> None:
    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination=destination,
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    await module.otp_verifier.execute(
        VerifyOtpCommand(
            challenge_id=registration.challenge_id,
            code=latest_otp(sender),
            full_name="Cooldown Security",
        )
    )


@pytest.mark.asyncio
async def test_repeated_login_request_returns_same_active_challenge_without_resending() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        await register_user(
            module=module,
            sender=sender,
            destination="cooldown@example.com",
        )
        sender.commands.clear()

        first = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="cooldown@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )
        second = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="cooldown@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )

        assert second.challenge_id == first.challenge_id
        assert second.expires_at == first.expires_at
        assert second.resend_available_at == first.resend_available_at
        assert len(sender.commands) == 1

        authenticated = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=second.challenge_id,
                code=latest_otp(sender),
            )
        )
        assert authenticated.user_id is not None
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_consumed_challenge_does_not_block_new_login_request() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        await register_user(
            module=module,
            sender=sender,
            destination="consumed@example.com",
        )
        sender.commands.clear()

        first = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="consumed@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )
        await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=first.challenge_id,
                code=latest_otp(sender),
            )
        )

        second = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="consumed@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )

        assert second.challenge_id != first.challenge_id
        assert len(sender.commands) == 2
    finally:
        await database.close()
