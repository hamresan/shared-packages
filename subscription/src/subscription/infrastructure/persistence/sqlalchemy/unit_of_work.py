from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import (
    PlanRepository,
    SubscriptionRepository,
    SubscriptionUnitOfWork,
    UsageRepository,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemySubscriptionRepositoryFactory,
)
from subscription.infrastructure.persistence.sqlalchemy.session import AsyncSessionFactory


class SqlAlchemySubscriptionUnitOfWork(SubscriptionUnitOfWork):
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        repository_factory: SqlAlchemySubscriptionRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory
        self._session_context: AbstractAsyncContextManager[AsyncSession] | None = None
        self._session: AsyncSession | None = None
        self._plans: PlanRepository | None = None
        self._subscriptions: SubscriptionRepository | None = None
        self._usage: UsageRepository | None = None

    @property
    def plans(self) -> PlanRepository:
        if self._plans is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._plans

    @property
    def subscriptions(self) -> SubscriptionRepository:
        if self._subscriptions is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._subscriptions

    @property
    def usage(self) -> UsageRepository:
        if self._usage is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._usage

    async def __aenter__(self) -> Self:
        self._session_context = self._session_factory()
        self._session = await self._session_context.__aenter__()
        repositories = self._repository_factory.create(self._session)
        self._plans = repositories.plans
        self._subscriptions = repositories.subscriptions
        self._usage = repositories.usage
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is not None and exc is not None:
            await self._session.rollback()
        if self._session_context is not None:
            await self._session_context.__aexit__(exc_type, exc, traceback)

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        await self._session.commit()


class SqlAlchemySubscriptionUnitOfWorkFactory:
    def __init__(
        self,
        session_factory: AsyncSessionFactory,
        repository_factory: SqlAlchemySubscriptionRepositoryFactory,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factory = repository_factory

    def __call__(self) -> SqlAlchemySubscriptionUnitOfWork:
        return SqlAlchemySubscriptionUnitOfWork(self._session_factory, self._repository_factory)
