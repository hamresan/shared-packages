from contextlib import AbstractAsyncContextManager
from datetime import datetime
from typing import Protocol
from uuid import UUID

from business.domain.business import Business
from business.domain.membership import BusinessMembership


class BusinessRepository(Protocol):
    async def add(self, business: Business) -> None: ...

    async def get_by_id(self, business_id: UUID) -> Business | None: ...

    async def list_by_ids(self, business_ids: tuple[UUID, ...]) -> tuple[Business, ...]: ...

    async def save(self, business: Business) -> None: ...


class BusinessMembershipRepository(Protocol):
    async def add(self, membership: BusinessMembership) -> None: ...

    async def get_by_business_and_user(
        self, business_id: UUID, user_id: UUID
    ) -> BusinessMembership | None: ...

    async def list_by_user_id(self, user_id: UUID) -> tuple[BusinessMembership, ...]: ...


class BusinessUnitOfWork(Protocol):
    @property
    def businesses(self) -> BusinessRepository: ...

    @property
    def memberships(self) -> BusinessMembershipRepository: ...

    async def commit(self) -> None: ...


class BusinessUnitOfWorkFactory(Protocol):
    def __call__(self) -> AbstractAsyncContextManager[BusinessUnitOfWork]: ...


class IdentifierGenerator(Protocol):
    def new_id(self) -> UUID: ...


class Clock(Protocol):
    def now(self) -> datetime: ...
