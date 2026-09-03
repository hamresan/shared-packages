"""Authorized downstream Instagram access tests."""

from asyncio import run
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from instagram_auth.application.access import (
    AuthorizedInstagramAccessTokenProvider,
    InstagramConnectionAccessPolicy,
)
from instagram_auth.application.errors import (
    InstagramConnectionPermissionError,
    InstagramConnectionUnavailableError,
)
from instagram_auth.application.health import InstagramConnectionHealthPolicy
from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from tests.application.access.fakes import (
    FakeInstagramAccessTokenProtector,
    FakeInstagramConnectionReader,
    FakeInstagramCredentialRepository,
)
from tests.application.contracts.fakes import FixedClock

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def build_connection(value: str, *, owner_user_id: str = "owner-1") -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(value)),
        owner_user_id=owner_user_id,
        instagram_account_id=value,
        username=value,
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
    )


def build_provider(
    connections: tuple[InstagramConnection, ...],
    credentials: tuple[InstagramProtectedCredential, ...],
) -> AuthorizedInstagramAccessTokenProvider:
    return AuthorizedInstagramAccessTokenProvider(
        FakeInstagramConnectionReader(connections),
        FakeInstagramCredentialRepository(credentials),
        FakeInstagramAccessTokenProtector(),
        InstagramConnectionAccessPolicy(FixedClock(NOW), InstagramConnectionHealthPolicy()),
    )


def test_provider_returns_token_for_selected_usable_connection() -> None:
    first = build_connection("00000000-0000-0000-0000-000000000201")
    second = build_connection("00000000-0000-0000-0000-000000000202")
    provider = build_provider(
        (first, second),
        (
            InstagramProtectedCredential(first.id, "protected:token-1"),
            InstagramProtectedCredential(second.id, "protected:token-2"),
        ),
    )

    token = run(
        provider.get_access_token(
            connection_id=second.id,
            required_permissions=(InstagramPermission.MANAGE_MESSAGES,),
        )
    )

    assert token == "token-2"


def test_provider_fails_closed_when_required_permission_is_missing() -> None:
    connection = build_connection("00000000-0000-0000-0000-000000000203")
    provider = build_provider(
        (connection,),
        (InstagramProtectedCredential(connection.id, "protected:token"),),
    )

    with pytest.raises(InstagramConnectionPermissionError):
        run(
            provider.get_access_token(
                connection_id=connection.id,
                required_permissions=(InstagramPermission.CONTENT_PUBLISH,),
            )
        )


def test_provider_fails_closed_for_disconnected_connection() -> None:
    connected = build_connection("00000000-0000-0000-0000-000000000204")
    connection = replace(connected, status=InstagramConnectionState.DISCONNECTED)
    provider = build_provider(
        (connection,),
        (InstagramProtectedCredential(connection.id, "protected:token"),),
    )

    with pytest.raises(InstagramConnectionUnavailableError):
        run(provider.get_access_token(connection_id=connection.id))


def test_provider_fails_closed_for_revoked_credential() -> None:
    connection = build_connection("00000000-0000-0000-0000-000000000205")
    provider = build_provider(
        (connection,),
        (
            InstagramProtectedCredential(
                connection.id,
                "protected:token",
                revoked_at=NOW,
            ),
        ),
    )

    with pytest.raises(InstagramConnectionUnavailableError):
        run(provider.get_access_token(connection_id=connection.id))


def test_provider_fails_closed_for_expired_connection_credential() -> None:
    connection = replace(
        build_connection("00000000-0000-0000-0000-000000000207"),
        credential_expires_at=NOW - timedelta(seconds=1),
    )
    provider = build_provider(
        (connection,),
        (InstagramProtectedCredential(connection.id, "protected:token"),),
    )

    with pytest.raises(InstagramConnectionUnavailableError):
        run(provider.get_access_token(connection_id=connection.id))


def test_provider_fails_closed_when_connection_does_not_exist() -> None:
    missing_id = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000206"))
    provider = build_provider((), ())

    with pytest.raises(InstagramConnectionUnavailableError):
        run(provider.get_access_token(connection_id=missing_id))
