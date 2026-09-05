"""Builders for FastAPI adapter tests."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import FastAPI
from starlette.testclient import TestClient

from instagram_auth.application.authorization.callback import ValidateInstagramAuthorizationCallback
from instagram_auth.application.authorization.factory import InstagramAuthorizationStateFactory
from instagram_auth.application.authorization.start import StartInstagramAuthorization
from instagram_auth.application.authorization.validation import InstagramAuthorizationStateValidator
from instagram_auth.application.connections import (
    DisconnectInstagramConnection,
    GetInstagramConnection,
    InstagramConnectionOwnershipPolicy,
    ListInstagramConnections,
    ReconnectInstagramConnection,
    StartInstagramConnectionReauthorization,
)
from instagram_auth.baseline import (
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
)
from instagram_auth.domain import InstagramConnection, InstagramConnectionId
from instagram_auth.presentation.fastapi import (
    InstagramConnectionResponseMapper,
    InstagramFastApiConfig,
    InstagramFastApiDependencies,
    InstagramFastApiErrorMapper,
    create_instagram_auth_router,
)
from tests.application.authorization.fakes import (
    FakeInstagramAuthorizationStateStore,
    FakeInstagramAuthorizationUrlBuilder,
)
from tests.application.connections.fakes import FakeConnectionStore, FakeInstagramAuthUnitOfWork
from tests.application.contracts.fakes import FixedClock, FixedStateGenerator
from tests.presentation.fastapi.fakes import (
    FakeInstagramFastApiCallbackResponder,
    FakeInstagramFastApiOwnerContext,
)

NOW = datetime(2026, 9, 3, 20, 0, tzinfo=UTC)
REDIRECT_URI = "https://app.example/instagram/callback"


@dataclass(frozen=True, slots=True)
class FastApiTestContext:
    client: TestClient
    store: FakeConnectionStore
    state_store: FakeInstagramAuthorizationStateStore
    callback_responder: FakeInstagramFastApiCallbackResponder
    url_builder: FakeInstagramAuthorizationUrlBuilder


def build_connection(value: int, owner_user_id: str) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId(UUID(int=value)),
        owner_user_id=owner_user_id,
        instagram_account_id=f"ig-{value}",
        username=f"account-{value}",
        account_type=InstagramAccountType.BUSINESS,
        permissions=frozenset({InstagramPermission.BASIC}),
        status=InstagramConnectionState.CONNECTED,
        connected_at=NOW,
    )


def build_test_context(
    *,
    owner_user_id: str | None = "owner-1",
    connections: tuple[InstagramConnection, ...] = (),
) -> FastApiTestContext:
    state_store = FakeInstagramAuthorizationStateStore()
    url_builder = FakeInstagramAuthorizationUrlBuilder()
    clock = FixedClock(NOW)
    start_authorization = StartInstagramAuthorization(
        state_factory=InstagramAuthorizationStateFactory(
            state_generator=FixedStateGenerator("secure-state"),
            clock=clock,
            lifetime=timedelta(minutes=10),
        ),
        state_store=state_store,
        url_builder=url_builder,
    )
    validate_callback = ValidateInstagramAuthorizationCallback(
        state_store=state_store,
        state_validator=InstagramAuthorizationStateValidator(clock=clock),
    )

    store = FakeConnectionStore(connections)
    unit_of_work = FakeInstagramAuthUnitOfWork(store)
    ownership_policy = InstagramConnectionOwnershipPolicy()
    callback_responder = FakeInstagramFastApiCallbackResponder()
    dependencies = InstagramFastApiDependencies(
        start_authorization=start_authorization,
        validate_callback=validate_callback,
        list_connections=ListInstagramConnections(store),
        get_connection=GetInstagramConnection(store, ownership_policy),
        disconnect_connection=DisconnectInstagramConnection(unit_of_work, ownership_policy),
        reconnect_connection=ReconnectInstagramConnection(unit_of_work, ownership_policy),
        start_connection_reauthorization=StartInstagramConnectionReauthorization(
            get_connection=GetInstagramConnection(store, ownership_policy),
            start_authorization=start_authorization,
        ),
        owner_context=FakeInstagramFastApiOwnerContext(owner_user_id),
        callback_responder=callback_responder,
        connection_mapper=InstagramConnectionResponseMapper(),
        error_mapper=InstagramFastApiErrorMapper(),
    )

    app = FastAPI()
    app.include_router(
        create_instagram_auth_router(
            config=InstagramFastApiConfig(redirect_uri=REDIRECT_URI),
            dependencies=dependencies,
        )
    )
    return FastApiTestContext(
        client=TestClient(app),
        store=store,
        state_store=state_store,
        callback_responder=callback_responder,
        url_builder=url_builder,
    )
