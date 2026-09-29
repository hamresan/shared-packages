from typing import Protocol
from uuid import UUID

from identity.domain import IdentityType, User

from identity.application.dto import (
    AuthSessionResult,
    DataRetentionCleanupResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)
from identity.application.dto_external import AuthenticateExternalIdentityCommand


class ExternalIdentityAuthenticator(Protocol):
    async def execute(
        self,
        command: AuthenticateExternalIdentityCommand,
    ) -> AuthSessionResult: ...


class OtpRequester(Protocol):
    async def execute(self, command: RequestOtpCommand) -> RequestOtpResult: ...


class OtpVerifier(Protocol):
    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult: ...


class SessionRefresher(Protocol):
    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult: ...


class SessionRevoker(Protocol):
    async def execute(self, refresh_token: str) -> None: ...


class SessionBulkRevoker(Protocol):
    async def execute(self, user_id: UUID) -> None: ...


class IdentityDataRetentionCleaner(Protocol):
    async def execute(self) -> DataRetentionCleanupResult: ...


class IdentityUserResolver(Protocol):
    async def resolve_user_id(self, identity_type: IdentityType, value: str) -> UUID | None: ...


class IdentityUserProfileWriter(Protocol):
    async def update_full_name(self, user_id: UUID, full_name: str) -> User: ...
