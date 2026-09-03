from asyncio import run
from datetime import UTC, datetime, timedelta

import pytest

from instagram_auth.application.authorization import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
    InstagramAuthorizationStateFactory,
    StartInstagramAuthorization,
    StartInstagramAuthorizationCommand,
)
from instagram_auth.baseline import CORE_PERMISSIONS, InstagramPermission
from tests.application.authorization.fakes import (
    FakeInstagramAuthorizationStateStore,
    FakeInstagramAuthorizationUrlBuilder,
)
from tests.application.contracts.fakes import FixedClock, FixedStateGenerator


NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def test_start_persists_state_and_builds_least_privilege_authorization_url() -> None:
    store = FakeInstagramAuthorizationStateStore()
    url_builder = FakeInstagramAuthorizationUrlBuilder()
    service = StartInstagramAuthorization(
        state_factory=InstagramAuthorizationStateFactory(
            state_generator=FixedStateGenerator("secure-state"),
            clock=FixedClock(NOW),
            lifetime=timedelta(minutes=10),
        ),
        state_store=store,
        url_builder=url_builder,
    )

    result = run(
        service.execute(
            StartInstagramAuthorizationCommand(
                redirect_uri="https://app.example/callback",
                correlation=InstagramAuthorizationCorrelation(
                    flow=InstagramAuthorizationFlow.LOGIN
                ),
                optional_permissions={InstagramPermission.MANAGE_INSIGHTS},
            )
        )
    )

    assert result.expires_at == NOW + timedelta(minutes=10)
    assert url_builder.state == "secure-state"
    assert url_builder.redirect_uri == "https://app.example/callback"
    assert url_builder.permissions == CORE_PERMISSIONS | {InstagramPermission.MANAGE_INSIGHTS}
    assert run(store.consume("secure-state")) is not None


def test_connect_account_requires_owner_correlation() -> None:
    factory = InstagramAuthorizationStateFactory(
        state_generator=FixedStateGenerator("state"),
        clock=FixedClock(NOW),
        lifetime=timedelta(minutes=10),
    )

    with pytest.raises(ValueError, match="owner_user_id"):
        factory.create(
            redirect_uri="https://app.example/callback",
            correlation=InstagramAuthorizationCorrelation(
                flow=InstagramAuthorizationFlow.CONNECT_ACCOUNT
            ),
        )


def test_login_rejects_owner_correlation() -> None:
    factory = InstagramAuthorizationStateFactory(
        state_generator=FixedStateGenerator("state"),
        clock=FixedClock(NOW),
        lifetime=timedelta(minutes=10),
    )

    with pytest.raises(ValueError, match="must not be set"):
        factory.create(
            redirect_uri="https://app.example/callback",
            correlation=InstagramAuthorizationCorrelation(
                flow=InstagramAuthorizationFlow.LOGIN,
                owner_user_id="owner-1",
            ),
        )
