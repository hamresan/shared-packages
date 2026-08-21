from subscription.infrastructure.persistence.sqlalchemy import SubscriptionBase


def test_subscription_metadata_owns_only_prefixed_tables() -> None:
    table_names = set(SubscriptionBase.metadata.tables)

    assert table_names == {
        "subscription_plan",
        "subscription_plan_entitlement",
        "subscription_subscription",
        "subscription_trial_policy",
        "subscription_trial_usage_condition",
        "subscription_usage_record",
    }
    assert all(name.startswith("subscription_") for name in table_names)
