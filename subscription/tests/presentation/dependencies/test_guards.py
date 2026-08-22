import pytest

from subscription import SubjectReference
from subscription.presentation.dependencies import (
    AuthenticatedActor,
    PlanManagementGuard,
    SubjectAccessGuard,
)
from subscription.presentation.errors import SubscriptionAuthorizationDeniedError
from tests.support.presentation.fakes import FakeSubscriptionAuthorizer


async def test_plan_management_guard_allows_authorized_actor() -> None:
    guard = PlanManagementGuard(FakeSubscriptionAuthorizer())

    await guard.ensure_allowed(AuthenticatedActor("actor-1"))


async def test_plan_management_guard_rejects_unauthorized_actor() -> None:
    guard = PlanManagementGuard(FakeSubscriptionAuthorizer(allow_plan_management=False))

    with pytest.raises(SubscriptionAuthorizationDeniedError):
        await guard.ensure_allowed(AuthenticatedActor("actor-1"))


async def test_subject_access_guard_checks_requested_subject() -> None:
    authorizer = FakeSubscriptionAuthorizer()
    guard = SubjectAccessGuard(authorizer)
    subject = SubjectReference("store", "store-1")

    await guard.ensure_allowed(AuthenticatedActor("actor-1"), subject)

    assert authorizer.checked_subjects == [subject]


async def test_subject_access_guard_rejects_unauthorized_subject() -> None:
    guard = SubjectAccessGuard(FakeSubscriptionAuthorizer(allow_subject_access=False))

    with pytest.raises(SubscriptionAuthorizationDeniedError):
        await guard.ensure_allowed(
            AuthenticatedActor("actor-1"),
            SubjectReference("store", "store-1"),
        )
