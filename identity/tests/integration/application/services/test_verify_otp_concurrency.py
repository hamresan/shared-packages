from functools import partial

import pytest

from identity.application.dto import AuthSessionResult, RequestOtpCommand, VerifyOtpCommand
from identity.application.errors import (
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
)
from identity.domain import IdentityType, OtpPurpose
from tests.support.concurrency import ConcurrentRunner
from tests.support.database_inspector import IdentityDatabaseInspector
from tests.support.integrations import FakeNotificationSender
from tests.support.module_builder import IdentityTestModuleBuilder
from tests.support.otp import invalid_otp_for, latest_otp
from tests.support.postgresql_database import PostgresqlIdentityDatabase


@pytest.mark.asyncio
async def test_concurrent_valid_verification_creates_only_one_session(
    postgres_database: PostgresqlIdentityDatabase,
) -> None:
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(postgres_database, sender)
    inspector = IdentityDatabaseInspector(postgres_database)
    runner = ConcurrentRunner()

    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination="c1-valid@example.com",
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    command = VerifyOtpCommand(
        challenge_id=registration.challenge_id,
        code=latest_otp(sender),
        full_name="C1 Concurrency Test",
    )

    results = await runner.run(
        [
            partial(module.otp_verifier.execute, command),
            partial(module.otp_verifier.execute, command),
        ]
    )

    successful_results = [result for result in results if isinstance(result, AuthSessionResult)]
    failed_results = [result for result in results if isinstance(result, BaseException)]

    assert len(successful_results) == 1, f"Concurrent verification results: {results!r}"
    assert len(failed_results) == 1, f"Concurrent verification results: {results!r}"
    assert isinstance(failed_results[0], OtpChallengeNotFoundError), (
        f"Unexpected concurrent verification failure: {failed_results[0]!r}"
    )
    assert await inspector.count_sessions() == 1


@pytest.mark.asyncio
async def test_concurrent_invalid_verification_preserves_attempt_accounting(
    postgres_database: PostgresqlIdentityDatabase,
) -> None:
    sender = FakeNotificationSender()
    module = IdentityTestModuleBuilder().build(postgres_database, sender)
    inspector = IdentityDatabaseInspector(postgres_database)
    runner = ConcurrentRunner()

    registration = await module.otp_requester.execute(
        RequestOtpCommand(
            identity_type=IdentityType.EMAIL,
            destination="c1-invalid@example.com",
            purpose=OtpPurpose.REGISTRATION,
        )
    )
    invalid_command = VerifyOtpCommand(
        challenge_id=registration.challenge_id,
        code=invalid_otp_for(latest_otp(sender)),
        full_name="C1 Concurrency Test",
    )

    results = await runner.run(
        [
            partial(module.otp_verifier.execute, invalid_command)
            for _ in range(module.config.otp_max_attempts)
        ]
    )

    assert all(isinstance(result, InvalidOtpError) for result in results), (
        f"Unexpected concurrent invalid-verification results: {results!r}"
    )
    assert (
        await inspector.get_otp_attempts_count(registration.challenge_id)
        == module.config.otp_max_attempts
    )

    with pytest.raises(OtpAttemptsExceededError):
        await module.otp_verifier.execute(invalid_command)
