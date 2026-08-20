import pytest

from identity.application.dto import RequestOtpCommand
from identity.application.errors import IdentityRateLimitExceededError
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder


@pytest.mark.asyncio
async def test_equivalent_email_forms_share_request_rate_limit_bucket() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)
    destinations = [" User@Example.com ", "user@example.com"]

    try:
        for index in range(module.config.otp_request_burst_limit):
            await module.otp_requester.execute(
                RequestOtpCommand(
                    identity_type=IdentityType.EMAIL,
                    destination=destinations[index % len(destinations)],
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
