import pytest

from identity.application.dto import RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidRefreshTokenError, RefreshTokenReuseError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    assert isinstance(value, str)
    return value


@pytest.mark.asyncio
async def test_refresh_token_reuse_revokes_active_family() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="refresh-security@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        authenticated = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=latest_otp(sender),
                full_name="Refresh Security",
            )
        )
        rotated = await module.session_refresher.execute(
            RefreshSessionCommand(refresh_token=authenticated.refresh_token)
        )

        with pytest.raises(RefreshTokenReuseError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token=authenticated.refresh_token)
            )

        with pytest.raises(InvalidRefreshTokenError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token=rotated.refresh_token)
            )
    finally:
        await database.close()
