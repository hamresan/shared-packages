from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from identity.application.dto import (
    AuthSessionResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)


class FakeOtpRequester:
    def __init__(self) -> None:
        self.command: RequestOtpCommand | None = None
        self.challenge_id = uuid4()

    async def execute(self, command: RequestOtpCommand) -> RequestOtpResult:
        self.command = command
        now = datetime.now(UTC)
        return RequestOtpResult(
            challenge_id=self.challenge_id,
            expires_at=now + timedelta(minutes=5),
            resend_available_at=now + timedelta(minutes=1),
        )


class FakeOtpVerifier:
    def __init__(self) -> None:
        self.command: VerifyOtpCommand | None = None

    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult:
        self.command = command
        return build_auth_result()


class FakeSessionRefresher:
    def __init__(self) -> None:
        self.command: RefreshSessionCommand | None = None

    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult:
        self.command = command
        return build_auth_result()


class FakeSessionRevoker:
    def __init__(self) -> None:
        self.refresh_token: str | None = None

    async def execute(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token


class FakeSessionBulkRevoker:
    def __init__(self) -> None:
        self.user_id: UUID | None = None

    async def execute(self, user_id: UUID) -> None:
        self.user_id = user_id


def build_auth_result() -> AuthSessionResult:
    now = datetime.now(UTC)
    return AuthSessionResult(
        user_id=uuid4(),
        session_id=uuid4(),
        access_token="access-token",
        access_token_expires_at=now + timedelta(minutes=15),
        refresh_token="r" * 48,
        refresh_token_expires_at=now + timedelta(days=30),
    )
