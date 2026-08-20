import pytest

from identity.application.dto import RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidOtpError, OtpAttemptsExceededError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.otp import invalid_otp_for, latest_otp


@pytest.mark.asyncio
async def test_verification_rejects_attempts_after_configured_limit() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="security@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        invalid_otp = invalid_otp_for(latest_otp(sender))

        for _ in range(module.config.otp_max_attempts):
            with pytest.raises(InvalidOtpError):
                await module.otp_verifier.execute(
                    VerifyOtpCommand(
                        challenge_id=registration.challenge_id,
                        code=invalid_otp,
                        full_name="Security Test",
                    )
                )

        with pytest.raises(OtpAttemptsExceededError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=registration.challenge_id,
                    code=invalid_otp,
                    full_name="Security Test",
                )
            )
    finally:
        await database.close()
