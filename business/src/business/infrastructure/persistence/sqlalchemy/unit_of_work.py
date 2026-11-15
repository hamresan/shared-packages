from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Self
from uuid import UUID

from business.application.contracts import (
    BranchRepository,
    BusinessMembershipRepository,
    BusinessRepository,
    BusinessUnitOfWork,
    BusinessUnitOfWorkFactory,
    MembershipAuditRepository,
    MembershipBranchAccessRepository,
)
from business.infrastructure.persistence.sqlalchemy.mappers import (
    BranchMapper,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
)
from business.infrastructure.persistence.sqlalchemy.models import BusinessModel
from business.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyBranchRepository,
    SqlAlchemyBusinessRepository,
    SqlAlchemyMembershipAuditRepository,
    SqlAlchemyMembershipBranchAccessRepository,
    SqlAlchemyMembershipRepository,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SqlAlchemyBusinessUnitOfWork(BusinessUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        business_mapper: BusinessMapper,
        branch_mapper: BranchMapper,
        membership_mapper: MembershipMapper,
        audit_mapper: MembershipAuditMapper,
    ) -> None:
        self._session_factory = session_factory
        self._business_mapper = business_mapper
        self._branch_mapper = branch_mapper
        self._membership_mapper = membership_mapper
        self._audit_mapper = audit_mapper
        self._session: AsyncSession | None = None
        self._businesses: BusinessRepository | None = None
        self._branches: BranchRepository | None = None
        self._memberships: BusinessMembershipRepository | None = None
        self._access: MembershipBranchAccessRepository | None = None
        self._audit: MembershipAuditRepository | None = None
        self._committed = False

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._businesses = SqlAlchemyBusinessRepository(self._session, self._business_mapper)
        self._branches = SqlAlchemyBranchRepository(self._session, self._branch_mapper)
        self._memberships = SqlAlchemyMembershipRepository(self._session, self._membership_mapper)
        self._access = SqlAlchemyMembershipBranchAccessRepository(self._session)
        self._audit = SqlAlchemyMembershipAuditRepository(self._session, self._audit_mapper)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._session is not None:
            try:
                if not self._committed:
                    await self._session.rollback()
            finally:
                await self._session.close()
                self._session = None

    @property
    def businesses(self) -> BusinessRepository:
        if self._businesses is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._businesses

    @property
    def branches(self) -> BranchRepository:
        if self._branches is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._branches

    @property
    def memberships(self) -> BusinessMembershipRepository:
        if self._memberships is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._memberships

    @property
    def membership_branch_access(self) -> MembershipBranchAccessRepository:
        if self._access is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._access

    @property
    def membership_audit(self) -> MembershipAuditRepository:
        if self._audit is None:
            raise RuntimeError("Unit of work has not been entered")
        return self._audit

    async def lock_business_membership(self, business_id: UUID) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        # PostgreSQL holds the business row lock until commit/rollback, serializing owner mutations.
        await self._session.scalar(
            select(BusinessModel.id).where(BusinessModel.id == business_id).with_for_update()
        )

    async def commit(self) -> None:
        if self._session is None:
            raise RuntimeError("Unit of work has not been entered")
        await self._session.commit()
        self._committed = True


class SqlAlchemyBusinessUnitOfWorkFactory(BusinessUnitOfWorkFactory):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        business_mapper: BusinessMapper,
        branch_mapper: BranchMapper,
        membership_mapper: MembershipMapper,
        audit_mapper: MembershipAuditMapper,
    ) -> None:
        self._session_factory = session_factory
        self._business_mapper = business_mapper
        self._branch_mapper = branch_mapper
        self._membership_mapper = membership_mapper
        self._audit_mapper = audit_mapper

    def __call__(self) -> AbstractAsyncContextManager[BusinessUnitOfWork]:
        return SqlAlchemyBusinessUnitOfWork(
            self._session_factory,
            self._business_mapper,
            self._branch_mapper,
            self._membership_mapper,
            self._audit_mapper,
        )
