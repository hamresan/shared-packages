from httpx import Response

from subscription import SubjectReference, UsageMetric, UsagePeriod
from tests.support.presentation.adapter_factory import (
    PLAN_ID,
    SUBSCRIPTION_ID,
    build_subscription_api_test_runtime,
)
from tests.support.presentation.client import subscription_test_client
from tests.support.presentation.fakes import FakeSubscriptionAuthorizer


async def create_base_plan(runtime: object) -> Response:
    adapter = runtime.adapter  # type: ignore[attr-defined]
    async with subscription_test_client(adapter) as client:
        return await client.post(
            "/subscription/plans",
            json={
                "code": "pro",
                "name": "Pro",
                "subscription_type": "base",
                "entitlements": [
                    {
                        "key": "analytics.advanced",
                        "value": {"value_type": "boolean", "value": True},
                    }
                ],
            },
        )


async def test_create_and_get_plan() -> None:
    runtime = build_subscription_api_test_runtime()

    response = await create_base_plan(runtime)

    assert response.status_code == 201
    assert response.json()["id"] == str(PLAN_ID)
    async with subscription_test_client(runtime.adapter) as client:
        get_response = await client.get(f"/subscription/plans/{PLAN_ID}")
    assert get_response.status_code == 200
    assert get_response.json()["code"] == "pro"


async def test_plan_management_requires_authorization() -> None:
    runtime = build_subscription_api_test_runtime(
        authorizer=FakeSubscriptionAuthorizer(allow_plan_management=False)
    )

    response = await create_base_plan(runtime)

    assert response.status_code == 403


async def test_create_subscription_authorizes_target_subject() -> None:
    runtime = build_subscription_api_test_runtime()
    await create_base_plan(runtime)

    async with subscription_test_client(runtime.adapter) as client:
        response = await client.post(
            "/subscription/subscriptions",
            json={
                "subject": {"subject_type": "store", "subject_id": "store-1"},
                "plan_id": str(PLAN_ID),
                "source": "trial",
                "trial_policy": {
                    "completion_mode": "any",
                    "max_duration_seconds": 1209600,
                    "usage_conditions": [
                        {"metric": "conversations", "limit": 100, "period": "trial"}
                    ],
                },
            },
        )

    assert response.status_code == 201
    assert response.json()["id"] == str(SUBSCRIPTION_ID)
    assert runtime.authorizer.checked_subjects == [SubjectReference("store", "store-1")]


async def test_subscription_lifecycle_and_entitlement_query() -> None:
    runtime = build_subscription_api_test_runtime()
    await create_base_plan(runtime)

    async with subscription_test_client(runtime.adapter) as client:
        created = await client.post(
            "/subscription/subscriptions",
            json={
                "subject": {"subject_type": "store", "subject_id": "store-1"},
                "plan_id": str(PLAN_ID),
                "source": "manual",
            },
        )
        activated = await client.post(
            f"/subscription/subscriptions/{SUBSCRIPTION_ID}/activate",
            json={},
        )
        fetched = await client.get(f"/subscription/subscriptions/{SUBSCRIPTION_ID}")
        entitlement = await client.get(
            "/subscription/entitlements",
            params={
                "subject_type": "store",
                "subject_id": "store-1",
                "key": "analytics.advanced",
            },
        )

    assert created.status_code == 201
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    assert fetched.status_code == 200
    assert entitlement.status_code == 200
    assert entitlement.json()["grants"][0]["value"] == {
        "value_type": "boolean",
        "value": True,
    }


async def test_trial_start_and_cancel() -> None:
    runtime = build_subscription_api_test_runtime()
    await create_base_plan(runtime)

    async with subscription_test_client(runtime.adapter) as client:
        await client.post(
            "/subscription/subscriptions",
            json={
                "subject": {"subject_type": "store", "subject_id": "store-1"},
                "plan_id": str(PLAN_ID),
                "source": "trial",
                "trial_policy": {
                    "completion_mode": "any",
                    "max_duration_seconds": 86400,
                },
            },
        )
        started = await client.post(f"/subscription/subscriptions/{SUBSCRIPTION_ID}/trial")
        cancelled = await client.post(f"/subscription/subscriptions/{SUBSCRIPTION_ID}/cancel")

    assert started.status_code == 200
    assert started.json()["status"] == "trialing"
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


async def test_usage_record_and_counter_query() -> None:
    runtime = build_subscription_api_test_runtime()
    subject = SubjectReference("store", "store-1")
    runtime.unit_of_work_factory.usage_repository.counters[
        (subject, UsageMetric("conversations"), UsagePeriod.WEEK)
    ] = 7

    async with subscription_test_client(runtime.adapter) as client:
        recorded = await client.post(
            "/subscription/usage",
            json={
                "subject": {"subject_type": "store", "subject_id": "store-1"},
                "metric": "conversations",
                "amount": 2,
            },
        )
        counter = await client.get(
            "/subscription/usage",
            params={
                "subject_type": "store",
                "subject_id": "store-1",
                "metric": "conversations",
                "period": "week",
            },
        )

    assert recorded.status_code == 201
    assert recorded.json()["amount"] == 2
    assert counter.status_code == 200
    assert counter.json()["consumed"] == 7


async def test_subject_access_denial_returns_forbidden() -> None:
    runtime = build_subscription_api_test_runtime(
        authorizer=FakeSubscriptionAuthorizer(allow_subject_access=False)
    )
    await create_base_plan(runtime)

    async with subscription_test_client(runtime.adapter) as client:
        response = await client.post(
            "/subscription/subscriptions",
            json={
                "subject": {"subject_type": "store", "subject_id": "store-1"},
                "plan_id": str(PLAN_ID),
                "source": "manual",
            },
        )

    assert response.status_code == 403


async def test_missing_subscription_returns_not_found() -> None:
    runtime = build_subscription_api_test_runtime()

    async with subscription_test_client(runtime.adapter) as client:
        response = await client.get(f"/subscription/subscriptions/{SUBSCRIPTION_ID}")

    assert response.status_code == 404
