from uuid import UUID

from business.application.contracts import (
    BranchRepository,
    BusinessMembershipRepository,
    BusinessRepository,
    MembershipAuditRepository,
    MembershipBranchAccessRepository,
)
from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.enums import MembershipStatus
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord
from business.infrastructure.persistence.sqlalchemy.mappers import (
    BranchMapper,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
)
from business.infrastructure.persistence.sqlalchemy.models import (
    BranchModel,
    BusinessModel,
    MembershipBranchAccessModel,
    MembershipModel,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBusinessRepository(BusinessRepository):
    def __init__(self, session: AsyncSession, mapper: BusinessMapper) -> None:
        self._session, self._mapper = session, mapper

    async def add(self, business: Business) -> None:
        self._session.add(self._mapper.to_model(business))
        await self._session.flush()

    async def get_by_id(self, business_id: UUID) -> Business | None:
        model = await self._session.get(BusinessModel, business_id)
        return self._mapper.to_domain(model) if model is not None else None

    async def list_by_ids(self, business_ids: tuple[UUID, ...]) -> tuple[Business, ...]:
        if not business_ids:
            return ()
        result = await self._session.scalars(
            select(BusinessModel).where(BusinessModel.id.in_(business_ids))
        )
        return tuple(self._mapper.to_domain(item) for item in result)

    async def save(self, business: Business) -> None:
        model = await self._session.get(BusinessModel, business.id)
        if model is None:
            raise ValueError("Business cannot be updated because it does not exist")
        self._mapper.update(model, business)


class SqlAlchemyMembershipRepository(BusinessMembershipRepository):
    def __init__(self, session: AsyncSession, mapper: MembershipMapper) -> None:
        self._session, self._mapper = session, mapper

    async def add(self, membership: BusinessMembership) -> None:
        self._session.add(self._mapper.to_model(membership))
        await self._session.flush()

    async def get_by_business_and_user(
        self, business_id: UUID, user_id: UUID
    ) -> BusinessMembership | None:
        model = await self._session.scalar(
            select(MembershipModel)
            .where(
                MembershipModel.business_id == business_id,
                MembershipModel.user_id == user_id,
                MembershipModel.status.in_(
                    (MembershipStatus.ACTIVE.value, MembershipStatus.INVITED.value)
                ),
            )
            .execution_options(populate_existing=True)
        )
        return self._mapper.to_domain(model) if model is not None else None

    async def list_by_user_id(self, user_id: UUID) -> tuple[BusinessMembership, ...]:
        result = await self._session.scalars(
            select(MembershipModel).where(
                MembershipModel.user_id == user_id,
                MembershipModel.status == MembershipStatus.ACTIVE.value,
            )
        )
        return tuple(self._mapper.to_domain(item) for item in result)

    async def get_for_business(
        self, business_id: UUID, membership_id: UUID
    ) -> BusinessMembership | None:
        model = await self._session.scalar(
            select(MembershipModel).where(
                MembershipModel.business_id == business_id, MembershipModel.id == membership_id
            )
        )
        return self._mapper.to_domain(model) if model is not None else None

    async def list_for_business(self, business_id: UUID) -> tuple[BusinessMembership, ...]:
        result = await self._session.scalars(
            select(MembershipModel).where(MembershipModel.business_id == business_id)
        )
        return tuple(self._mapper.to_domain(item) for item in result)

    async def count_active_owners(self, business_id: UUID) -> int:
        from business.domain.enums import MembershipRole

        result = await self._session.scalar(
            select(func.count())
            .select_from(MembershipModel)
            .where(
                MembershipModel.business_id == business_id,
                MembershipModel.role == MembershipRole.OWNER.value,
                MembershipModel.status == MembershipStatus.ACTIVE.value,
            )
        )
        return result or 0

    async def save(self, membership: BusinessMembership) -> None:
        model = await self._session.get(MembershipModel, membership.id)
        if model is None or model.business_id != membership.business_id:
            raise ValueError("Membership cannot be updated outside its business")
        self._mapper.update(model, membership)
        await self._session.flush()


class SqlAlchemyBranchRepository(BranchRepository):
    def __init__(self, session: AsyncSession, mapper: BranchMapper) -> None:
        self._session, self._mapper = session, mapper

    async def add(self, branch: Branch) -> None:
        self._session.add(self._mapper.to_model(branch))
        await self._session.flush()

    async def get_for_business(self, business_id: UUID, branch_id: UUID) -> Branch | None:
        model = await self._session.scalar(
            select(BranchModel).where(
                BranchModel.business_id == business_id, BranchModel.id == branch_id
            )
        )
        return self._mapper.to_domain(model) if model is not None else None

    async def list_for_business(
        self,
        business_id: UUID,
        *,
        city: str | None,
        country_code: str | None,
        allowed_branch_ids: tuple[UUID, ...] | None = None,
    ) -> tuple[Branch, ...]:
        if allowed_branch_ids == ():
            return ()
        query = select(BranchModel).where(BranchModel.business_id == business_id)
        if city is not None:
            query = query.where(BranchModel.city == city.casefold())
        if country_code is not None:
            query = query.where(BranchModel.country_code == country_code)
        if allowed_branch_ids is not None:
            query = query.where(BranchModel.id.in_(allowed_branch_ids))
        result = await self._session.scalars(query)
        return tuple(self._mapper.to_domain(item) for item in result)

    async def save(self, branch: Branch) -> None:
        model = await self._session.get(BranchModel, branch.id)
        if model is None or model.business_id != branch.business_id:
            raise ValueError("Branch cannot be updated outside its business")
        self._mapper.update(model, branch)


class SqlAlchemyMembershipBranchAccessRepository(MembershipBranchAccessRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_branch_ids(self, membership_id: UUID) -> tuple[UUID, ...]:
        result = await self._session.scalars(
            select(MembershipBranchAccessModel.branch_id).where(
                MembershipBranchAccessModel.membership_id == membership_id
            )
        )
        return tuple(result)

    async def replace(self, membership_id: UUID, branch_ids: tuple[UUID, ...]) -> None:
        membership = await self._session.get(MembershipModel, membership_id)
        if membership is None:
            raise ValueError("Membership does not exist")
        await self._session.execute(
            delete(MembershipBranchAccessModel).where(
                MembershipBranchAccessModel.membership_id == membership_id
            )
        )
        for branch_id in branch_ids:
            self._session.add(
                MembershipBranchAccessModel(
                    membership_id=membership_id,
                    branch_id=branch_id,
                    business_id=membership.business_id,
                )
            )


class SqlAlchemyMembershipAuditRepository(MembershipAuditRepository):
    def __init__(self, session: AsyncSession, mapper: MembershipAuditMapper) -> None:
        self._session, self._mapper = session, mapper

    async def add(self, record: MembershipAuditRecord) -> None:
        self._session.add(self._mapper.to_model(record))
        await self._session.flush()
