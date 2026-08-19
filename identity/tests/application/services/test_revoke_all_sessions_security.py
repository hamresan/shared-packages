import pytest

from identity.application.contracts.security_events import SecurityEventName
from identity.application.dto import RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidRefreshTokenError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.security_events import RecordingSecurityEventSink


def latest_otp(sender: FakeNotificationSender) -> str:
    value = sender.commands[-1].variables["otp"]
    assert isinstance(value, str)
    return value


@pytest.mark.asyncio
async def test_revoke_all_sessions_invalidates_every_user_session() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    security_events = RecordingSecurityEventSink()
    module = IdentityTestModuleBuilder().build(database, sender, security_events)

    try:
        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="recovery@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        first_session = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=latest_otp(sender),
                full_name="Recovery User",
            )
        )

        login = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="recovery@example.com",
                purpose=OtpPurpose.LOGIN,
            )
        )
        second_session = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=login.challenge_id,
                code=latest_otp(sender),
            )
        )

        await module.session_bulk_revoker.execute(first_session.user_id)

        for refresh_token in (first_session.refresh_token, second_session.refresh_token):
            with pytest.raises(InvalidRefreshTokenError):
                await module.session_refresher.execute(
                    RefreshSessionCommand(refresh_token=refresh_token)
                )

        revoke_all_events = [
            event
            for event in security_events.events
            if event.name is SecurityEventName.SESSIONS_REVOKED_ALL
        ]
        assert len(revoke_all_events) == 1
        assert revoke_all_events[0].user_id == first_session.user_id
    finally:
        await database.close()
