import pytest

from identity.application.dto import RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InactiveUserError
from identity.domain import IdentityType, OtpPurpose, UserStatus
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.users import SqlAlchemyUserStatusUpdater


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [UserStatus.PENDING, UserStatus.SUSPENDED, UserStatus.DISABLED])
async def test_login_rejects_non_active_user(status: UserStatus) -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)
    status_updater = SqlAlchemyUserStatusUpdater(database.session_factory)

    try:
        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="status@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        registered = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=str(sender.commands[-1].variables["otp"]),
                full_name="Status Test User",
            )
        )
        await status_updater.set_status(registered.user_id, status)

        login = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="status@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )

        with pytest.raises(InactiveUserError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=login.challenge_id,
                    code=str(sender.commands[-1].variables["otp"]),
                )
            )
    finally:
        await database.close()
