import pytest

from identity.application.dto import RequestOtpCommand
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


@pytest.mark.asyncio
async def test_notification_failure_does_not_leave_active_otp_challenge() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender(failures_remaining=1)
    module = IdentityTestModuleBuilder().build(database, sender)
    command = RequestOtpCommand(
        identity_type=IdentityType.MOBILE,
        destination="+96890000000",
        purpose=OtpPurpose.LOGIN,
    )

    try:
        with pytest.raises(RuntimeError, match="Notification dispatch failed"):
            await module.otp_requester.execute(command)

        result = await module.otp_requester.execute(command)

        assert result.challenge_id is not None
        assert len(sender.commands) == 2
    finally:
        await database.close()
