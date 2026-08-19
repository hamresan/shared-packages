from subscription import (
    EntitlementValueType,
    PlanStatus,
    SubscriptionSource,
    SubscriptionStatus,
    SubscriptionType,
    TrialCompletionMode,
    UsagePeriod,
)


def test_subscription_type_values_are_stable() -> None:
    assert SubscriptionType.BASE == "base"
    assert SubscriptionType.ADDON == "addon"


def test_subscription_source_values_cover_initial_sources() -> None:
    assert {source.value for source in SubscriptionSource} == {
        "paid",
        "trial",
        "manual",
        "promotional",
        "migrated",
    }


def test_subscription_status_values_cover_initial_lifecycle() -> None:
    assert {status.value for status in SubscriptionStatus} == {
        "pending",
        "trialing",
        "active",
        "cancelled",
        "expired",
    }


def test_plan_status_values_are_stable() -> None:
    assert {status.value for status in PlanStatus} == {"active", "inactive", "retired"}


def test_entitlement_value_types_are_stable() -> None:
    assert {value_type.value for value_type in EntitlementValueType} == {
        "boolean",
        "integer",
        "decimal",
        "string",
        "unlimited",
    }


def test_trial_completion_modes_are_stable() -> None:
    assert {mode.value for mode in TrialCompletionMode} == {"any", "all"}


def test_usage_period_values_cover_initial_metering_periods() -> None:
    assert {period.value for period in UsagePeriod} == {
        "lifetime",
        "day",
        "week",
        "month",
        "billing_period",
        "trial",
    }
