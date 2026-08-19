from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from identity import IdentityModuleConfig
from identity.domain import IdentityType, OtpPurpose, UserStatus
from identity.infrastructure.persistence.sqlalchemy.models import (
    OtpChallengeModel,
    SessionModel,
    UserModel,
)
from tests.support.authentication import FakeAccessTokenAuthenticator
from tests.support.database import SqliteIdentityDatabase
from tests.support.integrations import FakeAccessTokenIssuer, FakeNotificationSender
from tests.support.module_builder import TEST_SIGNING_SECRET
from identity import IdentityModule


@pytest.mark.asyncio
async def test_cleanup_deletes_only_old_records_in_bounded_batches() -> None:
    database = SqliteIdentityDatabase()
    await database.start()
    now = datetime.now(UTC)
    user_id = uuid4()

    module = IdentityModule(
        IdentityModuleConfig(
            session_factory=database.session_factory,
            notification_sender=FakeNotificationSender(),
            access_token_issuer=FakeAccessTokenIssuer(),
            access_token_authenticator=FakeAccessTokenAuthenticator(),
            signing_secret=TEST_SIGNING_SECRET,
            otp_challenge_retention=timedelta(days=7),
            session_retention=timedelta(days=30),
            retention_cleanup_batch_size=1,
        )
    )

    try:
        async with database.session_factory() as session:
            session.add(
                UserModel(
                    id=user_id,
                    full_name="Retention User",
                    status=UserStatus.ACTIVE,
                    created_at=now - timedelta(days=100),
                    updated_at=now - timedelta(days=100),
                )
            )
            for age_days in (20, 10):
                session.add(
                    OtpChallengeModel(
                        id=uuid4(),
                        user_id=None,
                        identity_id=None,
                        identifier_type=IdentityType.EMAIL,
                        normalized_destination=f"old-{age_days}@example.com",
                        destination_snapshot=f"old-{age_days}@example.com",
                        purpose=OtpPurpose.LOGIN,
                        code_hash="hash",
                        expires_at=now - timedelta(days=age_days),
                        resend_available_at=now - timedelta(days=age_days),
                        attempts_count=0,
                        max_attempts=5,
                        verified_at=None,
                        consumed_at=None,
                        created_at=now - timedelta(days=age_days),
                    )
                )
            session.add(
                OtpChallengeModel(
                    id=uuid4(),
                    user_id=None,
                    identity_id=None,
                    identifier_type=IdentityType.EMAIL,
                    normalized_destination="fresh@example.com",
                    destination_snapshot="fresh@example.com",
                    purpose=OtpPurpose.LOGIN,
                    code_hash="hash",
                    expires_at=now + timedelta(minutes=5),
                    resend_available_at=now,
                    attempts_count=0,
                    max_attempts=5,
                    verified_at=None,
                    consumed_at=None,
                    created_at=now,
                )
            )
            for age_days in (60, 45):
                session.add(
                    SessionModel(
                        id=uuid4(),
                        user_id=user_id,
                        refresh_token_hash=f"old-session-{age_days}",
                        family_id=uuid4(),
                        parent_session_id=None,
                        replaced_by_session_id=None,
                        expires_at=now - timedelta(days=age_days),
                        family_expires_at=now - timedelta(days=age_days),
                        revoked_at=None,
                        device_info=None,
                        ip_address=None,
                        created_at=now - timedelta(days=age_days),
                        last_used_at=None,
                    )
                )
            session.add(
                SessionModel(
                    id=uuid4(),
                    user_id=user_id,
                    refresh_token_hash="fresh-session",
                    family_id=uuid4(),
                    parent_session_id=None,
                    replaced_by_session_id=None,
                    expires_at=now + timedelta(days=10),
                    family_expires_at=now + timedelta(days=60),
                    revoked_at=None,
                    device_info=None,
                    ip_address=None,
                    created_at=now,
                    last_used_at=None,
                )
            )
            await session.commit()

        first = await module.data_retention_cleaner.execute()
        second = await module.data_retention_cleaner.execute()

        assert first.deleted_otp_challenges == 1
        assert first.deleted_sessions == 1
        assert second.deleted_otp_challenges == 1
        assert second.deleted_sessions == 1

        async with database.session_factory() as session:
            challenge_count = await session.scalar(select(func.count()).select_from(OtpChallengeModel))
            session_count = await session.scalar(select(func.count()).select_from(SessionModel))

        assert challenge_count == 1
        assert session_count == 1
    finally:
        await database.close()
