import pytest

from identity.application.contracts.security_events import SecurityEventName
from identity.application.dto import RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidOtpError, RefreshTokenReuseError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.security_events import RecordingSecurityEventSink


@pytest.mark.asyncio
async def test_failed_otp_and_session_revoke_emit_security_events() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    events = RecordingSecurityEventSink()
    module = IdentityTestModuleBuilder().build(database, sender, events)

    try:
        request = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="security-events@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )

        with pytest.raises(InvalidOtpError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=request.challenge_id,
                    code="000000",
                    full_name="Security Events",
                )
            )

        otp = str(sender.commands[-1].variables["otp"])
        session = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=request.challenge_id,
                code=otp,
                full_name="Security Events",
            )
        )
        await module.session_revoker.execute(session.refresh_token)

        assert [event.name for event in events.events] == [
            SecurityEventName.OTP_ATTEMPT_FAILED,
            SecurityEventName.SESSION_REVOKED,
        ]
        assert events.events[0].challenge_id == request.challenge_id
        assert events.events[1].session_id == session.session_id
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_refresh_reuse_emits_security_event() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    events = RecordingSecurityEventSink()
    module = IdentityTestModuleBuilder().build(database, sender, events)

    try:
        request = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="reuse-events@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        otp = str(sender.commands[-1].variables["otp"])
        session = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=request.challenge_id,
                code=otp,
                full_name="Reuse Events",
            )
        )

        await module.session_refresher.execute(
            RefreshSessionCommand(refresh_token=session.refresh_token)
        )
        with pytest.raises(RefreshTokenReuseError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token=session.refresh_token)
            )

        reuse_event = events.events[-1]
        assert reuse_event.name is SecurityEventName.REFRESH_REUSE_DETECTED
        assert reuse_event.user_id == session.user_id
        assert reuse_event.session_id == session.session_id
        assert reuse_event.family_id is not None
    finally:
        await database.close()
