from asyncio import run
from datetime import UTC, datetime, timedelta

import pytest

from instagram_auth.application.authorization.callback import (
    ValidateInstagramAuthorizationCallback,
)
from instagram_auth.application.authorization.models import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
    InstagramAuthorizationState,
)
from instagram_auth.application.authorization.validation import (
    InstagramAuthorizationStateValidationError,
    InstagramAuthorizationStateValidationFailure,
    InstagramAuthorizationStateValidator,
)
from tests.application.authorization.fakes import FakeInstagramAuthorizationStateStore
from tests.application.contracts.fakes import FixedClock

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
REDIRECT_URI = "https://app.example/callback"


def build_state(
    *,
    flow: InstagramAuthorizationFlow = InstagramAuthorizationFlow.LOGIN,
    owner_user_id: str | None = None,
    expires_at: datetime | None = None,
) -> InstagramAuthorizationState:
    return InstagramAuthorizationState(
        state="state-1",
        redirect_uri=REDIRECT_URI,
        correlation=InstagramAuthorizationCorrelation(
            flow=flow,
            owner_user_id=owner_user_id,
        ),
        expires_at=expires_at or NOW + timedelta(minutes=10),
    )


def build_service(
    store: FakeInstagramAuthorizationStateStore,
) -> ValidateInstagramAuthorizationCallback:
    return ValidateInstagramAuthorizationCallback(
        state_store=store,
        state_validator=InstagramAuthorizationStateValidator(clock=FixedClock(NOW)),
    )


def assert_failure(
    service: ValidateInstagramAuthorizationCallback,
    *,
    state: str | None,
    redirect_uri: str = REDIRECT_URI,
    owner_user_id: str | None = None,
    expected: InstagramAuthorizationStateValidationFailure,
) -> None:
    with pytest.raises(InstagramAuthorizationStateValidationError) as exc_info:
        run(
            service.execute(
                state=state,
                redirect_uri=redirect_uri,
                authenticated_owner_user_id=owner_user_id,
            )
        )
    assert exc_info.value.failure is expected


def test_valid_login_state_is_consumed_and_returns_trusted_correlation() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(store.save(build_state()))
    service = build_service(store)

    result = run(service.execute(state="state-1", redirect_uri=REDIRECT_URI))

    assert result.correlation.flow is InstagramAuthorizationFlow.LOGIN
    assert run(store.consume("state-1")) is None


def test_missing_state_is_rejected() -> None:
    assert_failure(
        build_service(FakeInstagramAuthorizationStateStore()),
        state=None,
        expected=InstagramAuthorizationStateValidationFailure.MISSING,
    )


def test_unknown_or_replayed_state_is_rejected() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(store.save(build_state()))
    service = build_service(store)
    run(service.execute(state="state-1", redirect_uri=REDIRECT_URI))

    assert_failure(
        service,
        state="state-1",
        expected=InstagramAuthorizationStateValidationFailure.NOT_FOUND_OR_REUSED,
    )


def test_expired_state_is_rejected() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(store.save(build_state(expires_at=NOW)))

    assert_failure(
        build_service(store),
        state="state-1",
        expected=InstagramAuthorizationStateValidationFailure.EXPIRED,
    )


def test_redirect_uri_mismatch_is_rejected_and_consumes_state() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(store.save(build_state()))
    service = build_service(store)

    assert_failure(
        service,
        state="state-1",
        redirect_uri="https://attacker.example/callback",
        expected=InstagramAuthorizationStateValidationFailure.REDIRECT_URI_MISMATCH,
    )
    assert run(store.consume("state-1")) is None


def test_connect_account_rejects_different_authenticated_owner() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(
        store.save(
            build_state(
                flow=InstagramAuthorizationFlow.CONNECT_ACCOUNT,
                owner_user_id="owner-1",
            )
        )
    )

    assert_failure(
        build_service(store),
        state="state-1",
        owner_user_id="owner-2",
        expected=InstagramAuthorizationStateValidationFailure.OWNER_MISMATCH,
    )


def test_connect_account_accepts_matching_authenticated_owner() -> None:
    store = FakeInstagramAuthorizationStateStore()
    run(
        store.save(
            build_state(
                flow=InstagramAuthorizationFlow.CONNECT_ACCOUNT,
                owner_user_id="owner-1",
            )
        )
    )

    result = run(
        build_service(store).execute(
            state="state-1",
            redirect_uri=REDIRECT_URI,
            authenticated_owner_user_id="owner-1",
        )
    )

    assert result.correlation.owner_user_id == "owner-1"
