from asyncio import run
from datetime import UTC, datetime
from uuid import UUID

import pytest

from instagram_auth.application.authorization import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
)
from instagram_auth.application.connections import InstagramConnectionOwnershipPolicy
from instagram_auth.application.credentials import InstagramProtectedCredentialFactory
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionIdentityMismatchError,
)
from instagram_auth.application.linking import (
    InstagramConnectionFactory,
    InstagramHostLinkAction,
    LinkInstagramAuthorization,
    LinkInstagramAuthorizationCommand,
    PrepareInstagramHostIdentityHandoff,
    ReauthorizeInstagramConnection,
    ReauthorizeInstagramConnectionCommand,
)
from instagram_auth.application.models import InstagramAuthorizationGrant
from instagram_auth.baseline import InstagramAccountType, InstagramPermission
from instagram_auth.domain import InstagramConnectionId, InstagramExternalIdentity
from tests.application.contracts.fakes import FixedClock
from tests.application.linking.fakes import (
    FakeInstagramAccessTokenProtector,
    FakeInstagramAuthUnitOfWork,
    FixedInstagramConnectionIdGenerator,
)

NOW = datetime(2026, 9, 3, tzinfo=UTC)
CONNECTION_ID = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000601"))
IDENTITY = InstagramExternalIdentity(
    provider_user_id="ig-professional-1",
    username="shop_one",
    account_type=InstagramAccountType.BUSINESS,
)
GRANT = InstagramAuthorizationGrant(
    access_token="raw-secret-token",
    granted_permissions=frozenset({InstagramPermission.BASIC}),
)


def test_login_handoff_requires_host_to_resolve_local_user() -> None:
    result = PrepareInstagramHostIdentityHandoff().execute(
        identity=IDENTITY,
        correlation=InstagramAuthorizationCorrelation(
            flow=InstagramAuthorizationFlow.LOGIN
        ),
    )

    assert result.action is InstagramHostLinkAction.RESOLVE_LOCAL_USER
    assert result.owner_user_id is None
    assert result.identity == IDENTITY


def test_connect_account_handoff_preserves_authenticated_owner() -> None:
    result = PrepareInstagramHostIdentityHandoff().execute(
        identity=IDENTITY,
        correlation=InstagramAuthorizationCorrelation(
            flow=InstagramAuthorizationFlow.CONNECT_ACCOUNT,
            owner_user_id="owner-1",
        ),
    )

    assert result.action is InstagramHostLinkAction.ATTACH_TO_EXISTING_OWNER
    assert result.owner_user_id == "owner-1"


def test_linking_second_account_keeps_connections_independent() -> None:
    unit_of_work = FakeInstagramAuthUnitOfWork()
    clock = FixedClock(NOW)
    service = LinkInstagramAuthorization(
        unit_of_work=unit_of_work,
        connection_factory=InstagramConnectionFactory(
            clock,
            FixedInstagramConnectionIdGenerator(CONNECTION_ID),
        ),
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )

    result = run(
        service.execute(
            LinkInstagramAuthorizationCommand(
                owner_user_id="owner-1",
                identity=IDENTITY,
                grant=GRANT,
            )
        )
    )

    stored = unit_of_work.connection_fake.connections[CONNECTION_ID]
    protected = unit_of_work.credential_fake.credentials[CONNECTION_ID]
    assert result.created is True
    assert result.owner_user_id == "owner-1"
    assert stored.instagram_account_id == IDENTITY.provider_user_id
    assert protected.protected_access_token == "protected:raw-secret-token"
    assert unit_of_work.committed is True


def test_returning_identity_refreshes_same_connection_for_host_owner() -> None:
    unit_of_work = FakeInstagramAuthUnitOfWork()
    clock = FixedClock(NOW)
    factory = InstagramConnectionFactory(
        clock,
        FixedInstagramConnectionIdGenerator(CONNECTION_ID),
    )
    service = LinkInstagramAuthorization(
        unit_of_work=unit_of_work,
        connection_factory=factory,
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )
    command = LinkInstagramAuthorizationCommand(
        owner_user_id="owner-1",
        identity=IDENTITY,
        grant=GRANT,
    )

    first = run(service.execute(command))
    second = run(service.execute(command))

    assert first.connection_id == second.connection_id
    assert second.created is False
    assert len(unit_of_work.connection_fake.connections) == 1


def test_selected_reauthorization_refreshes_same_connection() -> None:
    unit_of_work = FakeInstagramAuthUnitOfWork()
    clock = FixedClock(NOW)
    factory = InstagramConnectionFactory(
        clock,
        FixedInstagramConnectionIdGenerator(CONNECTION_ID),
    )
    linker = LinkInstagramAuthorization(
        unit_of_work=unit_of_work,
        connection_factory=factory,
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )
    run(
        linker.execute(
            LinkInstagramAuthorizationCommand(
                owner_user_id="owner-1",
                identity=IDENTITY,
                grant=GRANT,
            )
        )
    )

    refreshed_identity = InstagramExternalIdentity(
        provider_user_id=IDENTITY.provider_user_id,
        username="renamed_shop",
        account_type=InstagramAccountType.BUSINESS,
    )
    service = ReauthorizeInstagramConnection(
        unit_of_work=unit_of_work,
        ownership_policy=InstagramConnectionOwnershipPolicy(),
        connection_factory=factory,
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )
    result = run(
        service.execute(
            ReauthorizeInstagramConnectionCommand(
                owner_user_id="owner-1",
                connection_id=CONNECTION_ID,
                identity=refreshed_identity,
                grant=GRANT,
            )
        )
    )

    assert result.connection_id == CONNECTION_ID
    assert result.created is False
    assert (
        unit_of_work.connection_fake.connections[CONNECTION_ID].username
        == "renamed_shop"
    )
    assert len(unit_of_work.connection_fake.connections) == 1


def test_selected_reauthorization_rejects_different_instagram_identity() -> None:
    unit_of_work = FakeInstagramAuthUnitOfWork()
    clock = FixedClock(NOW)
    factory = InstagramConnectionFactory(
        clock,
        FixedInstagramConnectionIdGenerator(CONNECTION_ID),
    )
    linker = LinkInstagramAuthorization(
        unit_of_work=unit_of_work,
        connection_factory=factory,
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )
    run(
        linker.execute(
            LinkInstagramAuthorizationCommand(
                owner_user_id="owner-1",
                identity=IDENTITY,
                grant=GRANT,
            )
        )
    )
    different_identity = InstagramExternalIdentity(
        provider_user_id="ig-professional-other",
        username="other_shop",
        account_type=InstagramAccountType.BUSINESS,
    )
    service = ReauthorizeInstagramConnection(
        unit_of_work=unit_of_work,
        ownership_policy=InstagramConnectionOwnershipPolicy(),
        connection_factory=factory,
        credential_factory=InstagramProtectedCredentialFactory(
            FakeInstagramAccessTokenProtector(),
            clock,
        ),
    )

    with pytest.raises(InstagramConnectionIdentityMismatchError):
        run(
            service.execute(
                ReauthorizeInstagramConnectionCommand(
                    owner_user_id="owner-1",
                    connection_id=CONNECTION_ID,
                    identity=different_identity,
                    grant=GRANT,
                )
            )
        )
