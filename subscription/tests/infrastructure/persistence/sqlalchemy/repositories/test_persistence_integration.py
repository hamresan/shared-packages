from datetime import UTC, datetime, timedelta

from subscription import (
    SubjectReference,
    SubscriptionSource,
    SubscriptionStatus,
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
    UsageMetric,
    UsagePeriod,
    UsageRecord,
)
from subscription.infrastructure.persistence.sqlalchemy import (
    build_sqlalchemy_subscription_unit_of_work_factory,
)
from tests.infrastructure.persistence.sqlalchemy.support.database import SqliteTestDatabase
from tests.support.domain.plan_builder import PlanBuilder
from tests.support.domain.subscription_builder import SubscriptionBuilder


async def test_unit_of_work_persists_plan_subscription_trial_and_usage() -> None:
    database = SqliteTestDatabase()
    await database.create_schema()
    factory = build_sqlalchemy_subscription_unit_of_work_factory(database.session_factory())
    plan = PlanBuilder().build()
    subject = SubjectReference("store", "store-42")
    now = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)
    trial_policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
    )
    subscription = (
        SubscriptionBuilder()
        .with_subject(subject)
        .with_source(SubscriptionSource.TRIAL)
        .with_status(SubscriptionStatus.TRIALING)
        .with_started_at(now)
        .with_trial_policy(trial_policy)
        .with_trial_started_at(now)
        .build()
    )

    async with factory() as unit_of_work:
        await unit_of_work.plans.add(plan)
        await unit_of_work.subscriptions.add(subscription)
        await unit_of_work.usage.add(
            UsageRecord(subject, UsageMetric("conversations"), 7, now + timedelta(hours=1))
        )
        await unit_of_work.commit()

    async with factory() as unit_of_work:
        stored_plan = await unit_of_work.plans.get_by_id(plan.id)
        stored_subscription = await unit_of_work.subscriptions.get_by_id(subscription.id)
        counter = await unit_of_work.usage.get_counter(
            subject,
            UsageMetric("conversations"),
            UsagePeriod.TRIAL,
            now + timedelta(days=1),
        )

    assert stored_plan == plan
    assert stored_subscription is not None
    assert stored_subscription.trial_policy == trial_policy
    assert stored_subscription.source is SubscriptionSource.TRIAL
    assert counter.consumed == 7
    await database.dispose()
