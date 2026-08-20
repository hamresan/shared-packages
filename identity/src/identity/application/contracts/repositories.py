from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.domain import IdentityType, OtpChallenge, OtpPurpose, Session, User, UserIdentity


class UserRepository(Protocol):
    async def get(self, user_id: UUID) -> User | None: ...

    async def add(self, user: User) -> None: ...


class UserIdentityRepository(Protocol):
    async def get_by_destination(
        self,
        identity_type: IdentityType,
        normalized_value: str,
    ) -> UserIdentity | None: ...

    async def add(self, identity: UserIdentity) -> None: ...


class OtpChallengeRepository(Protocol):
    async def get_latest_active(
        self,
        destination: str,
        purpose: OtpPurpose,
        now: datetime,
    ) -> OtpChallenge | None: ...

    async def get(self, challenge_id: UUID) -> OtpChallenge | None: ...

    async def get_for_update(self, challenge_id: UUID) -> OtpChallenge | None: ...

    async def increment_attempts(self, challenge_id: UUID) -> None: ...

    async def delete_retained_before(self, cutoff: datetime, limit: int) -> int: ...

    async def add(self, challenge: OtpChallenge) -> None: ...

    async def save(self, challenge: OtpChallenge) -> None: ...


class SessionRepository(Protocol):
    async def get_by_refresh_token_hashes(
        self,
        refresh_token_hashes: Sequence[str],
    ) -> Session | None: ...

    async def get_for_update_by_refresh_token_hashes(
        self,
        refresh_token_hashes: Sequence[str],
    ) -> Session | None: ...

    async def revoke_family(self, family_id: UUID, revoked_at: datetime) -> None: ...

    async def revoke_all_by_user_id(self, user_id: UUID, revoked_at: datetime) -> None: ...

    async def delete_retained_before(self, cutoff: datetime, limit: int) -> int: ...

    async def add(self, session: Session) -> None: ...

    async def save(self, session: Session) -> None: ...
