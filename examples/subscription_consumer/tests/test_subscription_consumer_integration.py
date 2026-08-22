from datetime import UTC, datetime, timedelta
from uuid import UUID

from httpx import ASGITransport, AsyncClient

from subscription_consumer_app import build_subscription_runtime


async def test_consumer_wires_trial_paid_addon_usage_and_entitlements() -> None:
    runtime = build_subscription_runtime()
    await runtime.database.create_schema()
    transport = ASGITransport(app=runtime.app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            base_plan = await client.post(
                "/subscription/plans",
                json={
                    "code": "pro",
                    "name": "Pro",
                    "subscription_type": "base",
                    "entitlements": [
                        {
                            "key": "conversations.monthly",
                            "value": {"value_type": "integer", "value": 1000},
                        }
                    ],
                },
            )
            addon_plan = await client.post(
                "/subscription/plans",
                json={
                    "code": "analytics-addon",
                    "name": "Analytics Add-on",
                    "subscription_type": "addon",
                    "entitlements": [
                        {
                            "key": "analytics.advanced",
                            "value": {"value_type": "boolean", "value": True},
                        }
                    ],
                },
            )
            assert base_plan.status_code == 201
            assert addon_plan.status_code == 201

            trial = await client.post(
                "/subscription/subscriptions",
                json={
                    "subject": {"subject_type": "store", "subject_id": "store-1"},
                    "plan_id": base_plan.json()["id"],
                    "source": "trial",
                    "trial_policy": {
                        "completion_mode": "any",
                        "max_duration_seconds": 1209600,
                        "usage_conditions": [
                            {
                                "metric": "conversations",
                                "limit": 100,
                                "period": "trial",
                            }
                        ],
                    },
                },
            )
            trial_id = UUID(trial.json()["id"])
            started_trial = await client.post(f"/subscription/subscriptions/{trial_id}/trial")
            usage = await client.post(
                "/subscription/usage",
                json={
                    "subject": {"subject_type": "store", "subject_id": "store-1"},
                    "metric": "conversations",
                    "amount": 5,
                },
            )
            assert started_trial.json()["status"] == "trialing"
            assert usage.status_code == 201
            await client.post(f"/subscription/subscriptions/{trial_id}/cancel")

            paid = await client.post(
                "/subscription/subscriptions",
                json={
                    "subject": {"subject_type": "store", "subject_id": "store-1"},
                    "plan_id": base_plan.json()["id"],
                    "source": "paid",
                },
            )
            paid_id = UUID(paid.json()["id"])
            first_expiration = datetime.now(UTC) + timedelta(days=30)
            activated = await runtime.payment_events.activate_after_payment(
                paid_id,
                first_expiration,
            )
            renewed = await runtime.payment_events.renew_after_payment(
                paid_id,
                first_expiration + timedelta(days=30),
            )
            assert activated.status.value == "active"
            assert renewed.expires_at == first_expiration + timedelta(days=30)

            addon = await client.post(
                "/subscription/subscriptions",
                json={
                    "subject": {"subject_type": "store", "subject_id": "store-1"},
                    "plan_id": addon_plan.json()["id"],
                    "source": "manual",
                },
            )
            addon_id = UUID(addon.json()["id"])
            activated_addon = await client.post(
                f"/subscription/subscriptions/{addon_id}/activate",
                json={},
            )
            entitlement = await client.get(
                "/subscription/entitlements",
                params={
                    "subject_type": "store",
                    "subject_id": "store-1",
                    "key": "analytics.advanced",
                },
            )
            assert activated_addon.json()["status"] == "active"
            assert entitlement.json()["grants"][0]["value"] == {
                "value_type": "boolean",
                "value": True,
            }
    finally:
        await runtime.database.dispose()
