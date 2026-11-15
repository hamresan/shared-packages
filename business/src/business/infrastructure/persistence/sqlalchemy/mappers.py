from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.enums import (
    BranchAccessScope,
    BranchStatus,
    BusinessStatus,
    MembershipAuditAction,
    MembershipRole,
    MembershipStatus,
)
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord
from business.domain.value_objects import BranchAddress, BranchContact
from business.infrastructure.persistence.sqlalchemy.models import (
    BranchModel,
    BusinessModel,
    MembershipAuditModel,
    MembershipModel,
)


def utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


class BusinessMapper:
    def to_domain(self, model: BusinessModel) -> Business:
        return Business(
            id=model.id,
            name=model.name,
            business_type=model.business_type,
            country_code=model.country_code,
            default_language=model.default_language,
            default_currency_code=model.default_currency_code,
            created_at=utc(model.created_at) or model.created_at,
            updated_at=utc(model.updated_at) or model.updated_at,
            archived_at=utc(model.archived_at),
            status=BusinessStatus(model.status),
        )

    def to_model(self, entity: Business) -> BusinessModel:
        return BusinessModel(
            id=entity.id,
            name=entity.name,
            business_type=entity.business_type,
            country_code=entity.country_code,
            default_language=entity.default_language,
            default_currency_code=entity.default_currency_code,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def update(self, model: BusinessModel, entity: Business) -> None:
        model.name = entity.name
        model.business_type = entity.business_type
        model.updated_at = entity.updated_at
        model.archived_at = entity.archived_at
        model.status = entity.status.value


class BranchMapper:
    def to_domain(self, model: BranchModel) -> Branch:
        return Branch(
            id=model.id,
            business_id=model.business_id,
            name=model.name,
            timezone=model.timezone,
            address=BranchAddress(**model.address) if model.address else None,
            contact=BranchContact(**model.contact) if model.contact else None,
            status=BranchStatus(model.status),
            created_at=utc(model.created_at) or model.created_at,
            updated_at=utc(model.updated_at) or model.updated_at,
            archived_at=utc(model.archived_at),
        )

    def to_model(self, entity: Branch) -> BranchModel:
        return BranchModel(
            id=entity.id,
            business_id=entity.business_id,
            name=entity.name,
            timezone=entity.timezone,
            address=asdict(entity.address) if entity.address else None,
            contact=asdict(entity.contact) if entity.contact else None,
            city=entity.address.city.casefold() if entity.address and entity.address.city else None,
            country_code=entity.address.country_code if entity.address else None,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            archived_at=entity.archived_at,
        )

    def update(self, model: BranchModel, entity: Branch) -> None:
        incoming = self.to_model(entity)
        model.name = incoming.name
        model.timezone = incoming.timezone
        model.address = incoming.address
        model.contact = incoming.contact
        model.city = incoming.city
        model.country_code = incoming.country_code
        model.status = incoming.status
        model.updated_at = incoming.updated_at
        model.archived_at = incoming.archived_at


class MembershipMapper:
    def to_domain(self, model: MembershipModel) -> BusinessMembership:
        return BusinessMembership(
            id=model.id,
            business_id=model.business_id,
            user_id=model.user_id,
            role=MembershipRole(model.role),
            status=MembershipStatus(model.status),
            branch_access_scope=BranchAccessScope(model.branch_access_scope),
            created_at=utc(model.created_at) or model.created_at,
            updated_at=utc(model.updated_at) or model.updated_at,
        )

    def to_model(self, entity: BusinessMembership) -> MembershipModel:
        return MembershipModel(
            id=entity.id,
            business_id=entity.business_id,
            user_id=entity.user_id,
            role=entity.role.value,
            status=entity.status.value,
            branch_access_scope=entity.branch_access_scope.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def update(self, model: MembershipModel, entity: BusinessMembership) -> None:
        model.role = entity.role.value
        model.status = entity.status.value
        model.branch_access_scope = entity.branch_access_scope.value
        model.updated_at = entity.updated_at


class MembershipAuditMapper:
    def to_model(self, entity: MembershipAuditRecord) -> MembershipAuditModel:
        return MembershipAuditModel(
            id=entity.id,
            business_id=entity.business_id,
            membership_id=entity.membership_id,
            actor_user_id=entity.actor_user_id,
            action=entity.action.value,
            occurred_at=entity.occurred_at,
            previous_value=entity.previous_value,
            new_value=entity.new_value,
            branch_ids=[str(value) for value in entity.branch_ids],
        )

    def to_domain(self, model: MembershipAuditModel) -> MembershipAuditRecord:
        return MembershipAuditRecord(
            id=model.id,
            business_id=model.business_id,
            membership_id=model.membership_id,
            actor_user_id=model.actor_user_id,
            action=MembershipAuditAction(model.action),
            occurred_at=utc(model.occurred_at) or model.occurred_at,
            previous_value=model.previous_value,
            new_value=model.new_value,
            branch_ids=tuple(UUID(value) for value in model.branch_ids),
        )
