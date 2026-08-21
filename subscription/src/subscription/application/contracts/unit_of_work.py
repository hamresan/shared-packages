from types import TracebackType
from typing import Protocol

from subscription.application.contracts.repositories import (
    PlanRepository,
    SubscriptionRepository,
    UsageRepository,
)


class SubscriptionUnitOfWork(Protocol):
    @property
    def plans(self) -> PlanRepository: ...

    @property
    def subscriptions(self) -> SubscriptionRepository: ...

    @property
    def usage(self) -> UsageRepository: ...

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
