from types import TracebackType
from typing import Protocol

from subscription.application.contracts.repositories import (
    PlanRepository,
    SubscriptionRepository,
    UsageRepository,
)


class SubscriptionUnitOfWork(Protocol):
    plans: PlanRepository
    subscriptions: SubscriptionRepository
    usage: UsageRepository

    async def __aenter__(self) -> "SubscriptionUnitOfWork": ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    async def commit(self) -> None: ...


class SubscriptionUnitOfWorkFactory(Protocol):
    def __call__(self) -> SubscriptionUnitOfWork: ...
