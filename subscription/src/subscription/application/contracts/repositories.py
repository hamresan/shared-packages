from datetime import datetime
from typing import Protocol
from uuid import UUID

from subscription.domain import (
    Plan,
    PlanCode,
    SubjectReference,
    Subscription,
    UsageCounter,
    UsageMetric,
    UsagePeriod,
    UsageRecord,
)


class PlanRepository(Protocol):
    async def get_by_id(self, plan_id: UUID) -> Plan | None: ...

    async def get_by_code(self, code: PlanCode) -> Plan | None: ...

    async def add(self, plan: Plan) -> None: ...

    async def save(self, plan: Plan) -> None: ...


class SubscriptionRepository(Protocol):
    async def get_by_id(self, subscription_id: UUID) -> Subscription | None: ...

    async def list_for_subject(
        self,
        subject: SubjectReference,
    ) -> tuple[Subscription, ...]: ...

    async def add(self, subscription: Subscription) -> None: ...

    async def save(self, subscription: Subscription) -> None: ...


class UsageRepository(Protocol):
    async def add(self, record: UsageRecord) -> None: ...

    async def get_counter(
        self,
        subject: SubjectReference,
        metric: UsageMetric,
        period: UsagePeriod,
        at: datetime,
    ) -> UsageCounter: ...
