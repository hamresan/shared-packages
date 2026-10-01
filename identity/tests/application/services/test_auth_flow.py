from datetime import UTC, datetime
from uuid import uuid4

import pytest

from identity.application.dto import RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
    InvalidOtpError,
    InvalidRefreshTokenError,
    OtpChallengeNotFoundError,
    RegistrationNameRequiredError,
)
from identity.domain import IdentityType, OtpPurpose
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.otp import latest_otp


@pytest.mark.asyncio
async def test_registration_login_refresh_and_revoke_flow() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.MOBILE,
                destination="+968 9000 0000",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        registered = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=latest_otp(sender),
                full_name="Mehran",
                device_info="pytest",
                ip_address="127.0.0.1",
            )
        )

        login = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.MOBILE,
                destination="+96890000000",
                purpose=OtpPurpose.LOGIN,
            )
        )
        logged_in = await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=login.challenge_id,
                code=latest_otp(sender),
            )
        )
        refreshed = await module.session_refresher.execute(
            RefreshSessionCommand(refresh_token=logged_in.refresh_token)
        )
        await module.session_revoker.execute(refreshed.refresh_token)
        await module.session_revoker.execute(refreshed.refresh_token)

        assert registered.user_id == logged_in.user_id
        assert logged_in.session_id != refreshed.session_id
        assert logged_in.refresh_token != refreshed.refresh_token
        assert sender.commands[0].recipient == "+96890000000"
        assert sender.commands[0].template_key == "identity.otp"

        with pytest.raises(InvalidRefreshTokenError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token=refreshed.refresh_token)
            )
        with pytest.raises(InvalidRefreshTokenError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token="unknown-refresh-token" * 3)
            )
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_identity_flow_enforces_registration_login_and_otp_rules() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(database, sender)

    try:
        with pytest.raises(IdentityNotRegisteredError):
            await module.otp_requester.execute(
                RequestOtpCommand(
                    identity_type=IdentityType.EMAIL,
                    destination="missing@example.com",
                    purpose=OtpPurpose.LOGIN,
                )
            )
        assert sender.commands == []
        async with module.unit_of_work as uow:
            challenge = await uow.otp_challenges.get_latest_active(
                "missing@example.com",
                OtpPurpose.LOGIN,
                datetime.now(UTC),
            )
        assert challenge is None

        registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination=" User@Example.com ",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        repeated_registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="user@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        assert repeated_registration.challenge_id == registration.challenge_id

        with pytest.raises(RegistrationNameRequiredError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=registration.challenge_id,
                    code=latest_otp(sender),
                )
            )
        with pytest.raises(InvalidOtpError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=registration.challenge_id,
                    code="000000",
                    full_name="User",
                )
            )
        with pytest.raises(OtpChallengeNotFoundError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=uuid4(),
                    code="123456",
                    full_name="User",
                )
            )

        await module.otp_verifier.execute(
            VerifyOtpCommand(
                challenge_id=registration.challenge_id,
                code=latest_otp(sender),
                full_name="User",
            )
        )

        repeated_registration = await module.otp_requester.execute(
            RequestOtpCommand(
                identity_type=IdentityType.EMAIL,
                destination="user@example.com",
                purpose=OtpPurpose.REGISTRATION,
            )
        )
        with pytest.raises(IdentityAlreadyRegisteredError):
            await module.otp_verifier.execute(
                VerifyOtpCommand(
                    challenge_id=repeated_registration.challenge_id,
                    code=latest_otp(sender),
                    full_name="User",
                )
            )
    finally:
        await database.close()
