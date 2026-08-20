from functools import partial

import pytest

from identity.application.dto import AuthSessionResult, RefreshSessionCommand, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import InvalidRefreshTokenError, RefreshTokenReuseError
from identity.domain import IdentityType, OtpPurpose
from tests.support.concurrency import ConcurrentRunner
from tests.support.database_inspector import IdentityDatabaseInspector
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.otp import latest_otp
from tests.support.postgresql_database import PostgresqlIdentityDatabase


@pytest.mark.asyncio
async def test_concurrent_refresh_allows_single_rotation_and_revokes_family_on_reuse(
    postgres_database: PostgresqlIdentityDatabase,
) -> None:
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(postgres_database, sender)
    inspector = IdentityDatabaseInspector(postgres_database)
    runner = ConcurrentRunner()

    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination="h2-concurrent-refresh@example.com",
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    authenticated = await module.otp_verifier.execute(
        VerifyOtpCommand(
            challenge_id=registration.challenge_id,
            code=latest_otp(sender),
            full_name="H2 Concurrency Test",
        )
    )
    family_id = await inspector.get_session_family_id(authenticated.session_id)
    command = RefreshSessionCommand(refresh_token=authenticated.refresh_token)

    results = await runner.run(
        [
            partial(module.session_refresher.execute, command),
            partial(module.session_refresher.execute, command),
        ]
    )

    successful_results = [result for result in results if isinstance(result, AuthSessionResult)]
    failed_results = [result for result in results if isinstance(result, BaseException)]

    assert len(successful_results) == 1, f"Concurrent refresh results: {results!r}"
    assert len(failed_results) == 1, f"Concurrent refresh results: {results!r}"
    assert isinstance(failed_results[0], RefreshTokenReuseError), (
        f"Unexpected concurrent refresh failure: {failed_results[0]!r}"
    )
    assert await inspector.count_active_sessions_in_family(family_id) == 0

    rotated = successful_results[0]
    with pytest.raises(InvalidRefreshTokenError):
        await module.session_refresher.execute(
            RefreshSessionCommand(refresh_token=rotated.refresh_token)
        )


@pytest.mark.asyncio
async def test_refresh_rotation_preserves_absolute_family_expiration(
    postgres_database: PostgresqlIdentityDatabase,
) -> None:
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(postgres_database, sender)
    inspector = IdentityDatabaseInspector(postgres_database)

    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination="h2-family-expiry@example.com",
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    authenticated = await module.otp_verifier.execute(
        VerifyOtpCommand(
            challenge_id=registration.challenge_id,
            code=latest_otp(sender),
            full_name="H2 Family Expiry Test",
        )
    )
    original_family_expires_at = await inspector.get_session_family_expires_at(
        authenticated.session_id
    )

    first_rotation = await module.session_refresher.execute(
        RefreshSessionCommand(refresh_token=authenticated.refresh_token)
    )
    second_rotation = await module.session_refresher.execute(
        RefreshSessionCommand(refresh_token=first_rotation.refresh_token)
    )

    assert (
        await inspector.get_session_family_expires_at(first_rotation.session_id)
        == original_family_expires_at
    )
    assert (
        await inspector.get_session_family_expires_at(second_rotation.session_id)
        == original_family_expires_at
    )
