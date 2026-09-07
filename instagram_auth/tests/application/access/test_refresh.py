"""Automatic Instagram credential refresh tests."""

from asyncio import run
from datetime import UTC, datetime, timedelta
from uuid import UUID

from instagram_auth.application.access import (
    InstagramCredentialRefreshPolicy,
    RefreshingInstagramAccessTokenProvider,
    RefreshInstagramConnectionCredential,
)
from instagram_auth.application.credentials import InstagramProtectedCredentialFactory
from instagram_auth.application.models import (
    InstagramAuthorizationGrant,
    InstagramProtectedCredential,
)
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from tests.application.access.fakes import FakeInstagramAccessTokenProtector
from tests.application.access.refresh_fakes import (
    FakeAccessTokenProvider,
    FakeAccessTokenRefresher,
    FakeConnectionRepository,
    FakeCredentialRepository,
    FakeInstagramAuthUnitOfWork,
)
from tests.application.contracts.fakes import FixedClock

NOW = datetime(2026, 9, 7, tzinfo=UTC)


def build_connection(*, expires_at: datetime) -> InstagramConnection:
    connection_id = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000301"))
    return InstagramConnection(
        id=connection_id,
        owner_user_id="owner-1",
        instagram_account_id="account-1",
        username="store",
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW - timedelta(days=30),
        credential_expires_at=expires_at,
    )


def test_refresh_policy_only_refreshes_still_valid_tokens_near_expiry() -> None:
    policy = InstagramCredentialRefreshPolicy(timedelta(days=7))

    assert policy.should_refresh(expires_at=NOW + timedelta(days=2), now=NOW)
    assert not policy.should_refresh(expires_at=NOW + timedelta(days=10), now=NOW)
    assert not policy.should_refresh(expires_at=NOW - timedelta(seconds=1), now=NOW)
    assert not policy.should_refresh(expires_at=None, now=NOW)


def test_refreshes_and_persists_near_expiry_credential() -> None:
    connection = build_connection(expires_at=NOW + timedelta(days=2))
    old_credential = InstagramProtectedCredential(
        connection.id,
        "protected:old-token",
        expires_at=connection.credential_expires_at,
    )
    connections = FakeConnectionRepository(connection)
    credentials = FakeCredentialRepository(old_credential)
    unit_of_work = FakeInstagramAuthUnitOfWork(
        connections=connections,
        credentials=credentials,
    )
    refreshed_expiry = NOW + timedelta(days=60)
    token_refresher = FakeAccessTokenRefresher(
        InstagramAuthorizationGrant(
            access_token="new-token",
            expires_at=refreshed_expiry,
        )
    )
    protector = FakeInstagramAccessTokenProtector()
    service = RefreshInstagramConnectionCredential(
        unit_of_work=unit_of_work,
        token_refresher=token_refresher,
        token_protector=protector,
        credential_factory=InstagramProtectedCredentialFactory(
            token_protector=protector,
            clock=FixedClock(NOW),
        ),
        refresh_policy=InstagramCredentialRefreshPolicy(timedelta(days=7)),
        clock=FixedClock(NOW),
    )

    refreshed = run(service.execute(connection_id=connection.id))

    assert refreshed
    assert token_refresher.calls == ["old-token"]
    assert credentials.credential.protected_access_token == "protected:new-token"
    assert credentials.credential.expires_at == refreshed_expiry
    assert connections.connection.credential_expires_at == refreshed_expiry
    assert unit_of_work.commits == 1


def test_skips_refresh_when_credential_is_not_near_expiry() -> None:
    connection = build_connection(expires_at=NOW + timedelta(days=30))
    credential = InstagramProtectedCredential(
        connection.id,
        "protected:current-token",
        expires_at=connection.credential_expires_at,
    )
    unit_of_work = FakeInstagramAuthUnitOfWork(
        connections=FakeConnectionRepository(connection),
        credentials=FakeCredentialRepository(credential),
    )
    token_refresher = FakeAccessTokenRefresher(
        InstagramAuthorizationGrant("unused-token", NOW + timedelta(days=60))
    )
    protector = FakeInstagramAccessTokenProtector()
    service = RefreshInstagramConnectionCredential(
        unit_of_work=unit_of_work,
        token_refresher=token_refresher,
        token_protector=protector,
        credential_factory=InstagramProtectedCredentialFactory(
            token_protector=protector,
            clock=FixedClock(NOW),
        ),
        refresh_policy=InstagramCredentialRefreshPolicy(timedelta(days=7)),
        clock=FixedClock(NOW),
    )

    refreshed = run(service.execute(connection_id=connection.id))

    assert not refreshed
    assert token_refresher.calls == []
    assert unit_of_work.commits == 0


def test_refreshing_provider_maintains_credential_before_delegating_access() -> None:
    connection = build_connection(expires_at=NOW + timedelta(days=30))
    credential = InstagramProtectedCredential(
        connection.id,
        "protected:current-token",
        expires_at=connection.credential_expires_at,
    )
    unit_of_work = FakeInstagramAuthUnitOfWork(
        connections=FakeConnectionRepository(connection),
        credentials=FakeCredentialRepository(credential),
    )
    token_refresher = FakeAccessTokenRefresher(
        InstagramAuthorizationGrant("unused-token", NOW + timedelta(days=60))
    )
    protector = FakeInstagramAccessTokenProtector()
    refresher = RefreshInstagramConnectionCredential(
        unit_of_work=unit_of_work,
        token_refresher=token_refresher,
        token_protector=protector,
        credential_factory=InstagramProtectedCredentialFactory(
            token_protector=protector,
            clock=FixedClock(NOW),
        ),
        refresh_policy=InstagramCredentialRefreshPolicy(timedelta(days=7)),
        clock=FixedClock(NOW),
    )
    delegate = FakeAccessTokenProvider("current-token")
    provider = RefreshingInstagramAccessTokenProvider(
        delegate=delegate,
        credential_refresher=refresher,
    )

    token = run(
        provider.get_access_token(
            connection_id=connection.id,
            required_permissions=(InstagramPermission.MANAGE_MESSAGES,),
        )
    )

    assert token == "current-token"
    assert delegate.calls == [connection.id]
