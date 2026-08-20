from functools import partial

import pytest

from identity.application.dto import (
    AuthSessionResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    VerifyOtpCommand,
)
from identity.application.errors import InvalidRefreshTokenError
from identity.domain import IdentityType, OtpPurpose
from tests.support.concurrency import ConcurrentRunner
from tests.support.database_inspector import IdentityDatabaseInspector
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.otp import latest_otp
from tests.support.postgresql_database import PostgresqlIdentityDatabase


@pytest.mark.asyncio
async def test_concurrent_refresh_and_revoke_leave_no_active_session_in_family(
    postgres_database: PostgresqlIdentityDatabase,
) -> None:
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(postgres_database, sender)
    inspector = IdentityDatabaseInspector(postgres_database)
    runner = ConcurrentRunner()

    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination="r6-revoke-race@example.com",
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    authenticated = await module.otp_verifier.execute(
        VerifyOtpCommand(
            challenge_id=registration.challenge_id,
            code=latest_otp(sender),
            full_name="R6 Revoke Race Test",
        )
    )
    family_id = await inspector.get_session_family_id(authenticated.session_id)

    results = await runner.run(
        [
            partial(
                module.session_refresher.execute,
                RefreshSessionCommand(refresh_token=authenticated.refresh_token),
            ),
            partial(module.session_revoker.execute, authenticated.refresh_token),
        ]
    )

    refresh_result = results[0]
    revoke_result = results[1]

    assert revoke_result is None, f"Concurrent revoke failed: {revoke_result!r}"
    assert isinstance(refresh_result, (AuthSessionResult, InvalidRefreshTokenError)), (
        f"Unexpected concurrent refresh result: {refresh_result!r}"
    )
    assert await inspector.count_active_sessions_in_family(family_id) == 0

    if isinstance(refresh_result, AuthSessionResult):
        with pytest.raises(InvalidRefreshTokenError):
            await module.session_refresher.execute(
                RefreshSessionCommand(refresh_token=refresh_result.refresh_token)
            )
