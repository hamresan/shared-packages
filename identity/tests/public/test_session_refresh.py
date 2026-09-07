from datetime import UTC, datetime
from uuid import UUID

import pytest

from identity.application.dto import AuthSessionResult, RefreshSessionCommand
from identity.application.errors import IdentityError, InvalidRefreshTokenError
from identity.public import (
    PublicSessionRefresher,
    SessionRefreshError,
    SessionRefreshRejectedError,
)
from identity.public.services import SessionRefresher


class FakeSessionRefresher(SessionRefresher):
    def __init__(self) -> None:
        self.error: Exception | None = None
        self.result = AuthSessionResult(
            user_id=UUID("00000000-0000-0000-0000-000000000501"),
            session_id=UUID("00000000-0000-0000-0000-000000000502"),
            access_token="access-token",
            access_token_expires_at=datetime(2026, 9, 7, 12, 15, tzinfo=UTC),
            refresh_token="refresh-token",
            refresh_token_expires_at=datetime(2026, 10, 7, 12, 0, tzinfo=UTC),
        )

    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult:
        del command
        if self.error is not None:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test_public_refresher_returns_application_result() -> None:
    delegate = FakeSessionRefresher()

    result = await PublicSessionRefresher(delegate).execute(
        RefreshSessionCommand(refresh_token="r" * 32)
    )

    assert result is delegate.result


@pytest.mark.asyncio
async def test_public_refresher_normalizes_rejected_refresh_credentials() -> None:
    delegate = FakeSessionRefresher()
    delegate.error = InvalidRefreshTokenError("invalid")

    with pytest.raises(SessionRefreshRejectedError):
        await PublicSessionRefresher(delegate).execute(
            RefreshSessionCommand(refresh_token="r" * 32)
        )


@pytest.mark.asyncio
async def test_public_refresher_normalizes_other_identity_failures() -> None:
    delegate = FakeSessionRefresher()
    delegate.error = IdentityError("failed")

    with pytest.raises(SessionRefreshError):
        await PublicSessionRefresher(delegate).execute(
            RefreshSessionCommand(refresh_token="r" * 32)
        )
