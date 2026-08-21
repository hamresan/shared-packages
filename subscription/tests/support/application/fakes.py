from datetime import UTC, datetime
from types import TracebackType
from uuid import UUID

from subscription import (
    Plan,
    PlanCode,
    SubjectReference,
    Subscription,
    UsageCounter,
    UsageMetric,
    UsagePeriod,
    UsageRecord,
)
from subscription.application import (
    Clock,
    IdentifierGenerator,
    PlanRepository,
    SubscriptionRepository,
    SubscriptionUnitOfWork,
    SubscriptionUnitOfWorkFactory,
    UsageRepository,
)


class FixedClock(Clock):
    def __init__(self, value: datetime | None = None) -> None:
        self.value = value or datetime(2026, 8, 21, 12, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self.value


class FixedIdentifierGenerator(IdentifierGenerator):
    def __init__(self, value: UUID) -> None:
        self.value = value

    def new_id(self) -> UUID:
        return self.value


class FakePlanRepository(PlanRepository):
    def __init__(self, plans: tuple[Plan, ...] = ()) -> None:
        self.items = {plan.id: plan for plan in plans}

    async def get_by_id(self, plan_id: UUID) -> Plan | None:
        return self.items.get(plan_id)

    async def get_by_code(self, code: PlanCode) -> Plan | None:
        return next((plan for plan in self.items.values() if plan.code == code), None)

    async def add(self, plan: Plan) -> None:
        self.items[plan.id] = plan

    async def save(self, plan: Plan) -> None:
        self.items[plan.id] = plan


class FakeSubscriptionRepository(SubscriptionRepository):
    def __init__(self, subscriptions: tuple[Subscription, ...] = ()) -> None:
        self.items = {subscription.id: subscription for subscription in subscriptions}

    async def get_by_id(self, subscription_id: UUID) -> Subscription | None:
        return self.items.get(subscription_id)

    async def list_for_subject(
        self,
        subject: SubjectReference,
    ) -> tuple[Subscription, ...]:
        return tuple(item for item in self.items.values() if item.subject == subject)

    async def add(self, subscription: Subscription) -> None:
        self.items[subscription.id] = subscription

    async def save(self, subscription: Subscription) -> None:
        self.items[subscription.id] = subscription


class FakeUsageRepository(UsageRepository):
    def __init__(self) -> None:
        self.records: list[UsageRecord] = []
        self.counters: dict[tuple[SubjectReference, UsageMetric, UsagePeriod], int] = {}

    async def add(self, record: UsageRecord) -> None:
        self.records.append(record)

    async def get_counter(
        self,
        subject: SubjectReference,
        metric: UsageMetric,
        period: UsagePeriod,
        at: datetime,
    ) -> UsageCounter:
        del at
        consumed = self.counters.get((subject, metric, period), 0)
        return UsageCounter(metric=metric, period=period, consumed=consumed)


class FakeSubscriptionUnitOfWork(SubscriptionUnitOfWork):
    def __init__(
        self,
        plans: PlanRepository,
        subscriptions: SubscriptionRepository,
        usage: UsageRepository,
    ) -> None:
        self._plans = plans
        self._subscriptions = subscriptions
        self._usage = usage
        self.commit_count = 0

    @property
    def plans(self) -> PlanRepository:
        return self._plans

    @property
    def subscriptions(self) -> SubscriptionRepository:
        return self._subscriptions

    @property
    def usage(self) -> UsageRepository:
        return self._usage

    async def __aenter__(self) -> "FakeSubscriptionUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exc_type, exc_value, traceback

    async def commit(self) -> None:
        self.commit_count += 1


class FakeSubscriptionUnitOfWorkFactory(SubscriptionUnitOfWorkFactory):
    def __init__(
        self,
        plans: tuple[Plan, ...] = (),
        subscriptions: tuple[Subscription, ...] = (),
    ) -> None:
        self.plan_repository = FakePlanRepository(plans)
        self.subscription_repository = FakeSubscriptionRepository(subscriptions)
        self.usage_repository = FakeUsageRepository()
        self.unit_of_work = FakeSubscriptionUnitOfWork(
            self.plan_repository,
            self.subscription_repository,
            self.usage_repository,
        )

    def __call__(self) -> SubscriptionUnitOfWork:
        return self.unit_of_work
