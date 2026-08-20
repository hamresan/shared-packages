import pytest

from identity.application.dto import RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidRefreshTokenError, RefreshTokenReuseError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder

OLD_SIGNING_SECRET = b"old-identity-signing-secret-32-bytes!!"
NEW_SIGNING_SECRET = b"new-identity-signing-secret-32-bytes!!"


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


@pytest.mark.asyncio
async def test_refresh_token_remains_valid_during_hmac_key_rotation() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    old_module = IdentityTestModuleBuilder().build(
        database,
        sender,
        signing_secret=OLD_SIGNING_SECRET,
        signing_key_id="2026-07",
    )

    try:
        registration = await old_module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="rotation@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        authenticated = await old_module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=latest_otp(sender),
                full_name="Rotation Test",
            )
        )

        rotated_module = IdentityTestModuleBuilder().build(
            database,
            sender,
            signing_secret=NEW_SIGNING_SECRET,
            signing_key_id="2026-08",
            previous_signing_secrets={"2026-07": OLD_SIGNING_SECRET},
        )
        refreshed = await rotated_module.session_refresher.execute(
            RefreshSessionCommand(refresh_token=authenticated.refresh_token)
        )

        assert refreshed.user_id == authenticated.user_id
        assert refreshed.session_id != authenticated.session_id
        assert refreshed.refresh_token != authenticated.refresh_token
    finally:
        await database.close()
