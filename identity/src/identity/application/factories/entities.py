from datetime import datetime, timedelta
from uuid import UUID, uuid4

from identity.domain import (
    IdentityType,
    OtpChallenge,
    OtpPurpose,
    Session,
    User,
    UserIdentity,
    UserStatus,
)


class OtpChallengeFactory:
    def __init__(
        self,
        ttl: timedelta,
        resend_delay: timedelta,
        max_attempts: int,
    ) -> None:
        self._ttl = ttl
        self._resend_delay = resend_delay
        self._max_attempts = max_attempts

    def create(
        self,
        *,
        now: datetime,
        identity_type: IdentityType,
        destination: str,
        purpose: OtpPurpose,
        code_hash: str,
        user_id: UUID | None,
        identity_id: UUID | None,
    ) -> OtpChallenge:
        return OtpChallenge(
            id=uuid4(),
            user_id=user_id,
            identity_id=identity_id,
            identifier_type=identity_type,
            normalized_destination=destination,
            destination_snapshot=destination,
            purpose=purpose,
            code_hash=code_hash,
            expires_at=now + self._ttl,
            resend_available_at=now + self._resend_delay,
            attempts_count=0,
            max_attempts=self._max_attempts,
            verified_at=None,
            consumed_at=None,
            created_at=now,
        )


class UserRegistrationFactory:
    def create(
        self,
        *,
        now: datetime,
        full_name: str,
        identity_type: IdentityType,
        destination: str,
    ) -> tuple[User, UserIdentity]:
        user_id = uuid4()
        user = User(
            id=user_id,
            full_name=full_name,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        identity = UserIdentity(
            id=uuid4(),
            user_id=user_id,
            type=identity_type,
            value=destination,
            normalized_value=destination,
            verified_at=now,
            created_at=now,
            updated_at=now,
        )
        return user, identity


class SessionFactory:
    def __init__(self, ttl: timedelta) -> None:
        self._ttl = ttl

    def create(
        self,
        *,
        now: datetime,
        user_id: UUID,
        refresh_token_hash: str,
        device_info: str | None,
        ip_address: str | None,
        family_id: UUID | None = None,
        parent_session_id: UUID | None = None,
    ) -> Session:
        return Session(
            id=uuid4(),
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            family_id=family_id or uuid4(),
            parent_session_id=parent_session_id,
            replaced_by_session_id=None,
            expires_at=now + self._ttl,
            revoked_at=None,
            device_info=device_info,
            ip_address=ip_address,
            created_at=now,
            last_used_at=None,
        )
