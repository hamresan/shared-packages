from dataclasses import dataclass, field
from uuid import UUID

from business.domain.branch import Branch
from business.domain.business import Business
from business.domain.membership import BusinessMembership
from business.domain.membership_audit import MembershipAuditRecord


@dataclass(slots=True)
class InMemoryBusinessDatabase:
    businesses: dict[UUID, Business] = field(default_factory=dict[UUID, Business])
    branches: dict[UUID, Branch] = field(default_factory=dict[UUID, Branch])
    memberships: dict[UUID, BusinessMembership] = field(
        default_factory=dict[UUID, BusinessMembership]
    )
    membership_branch_ids: dict[UUID, tuple[UUID, ...]] = field(
        default_factory=dict[UUID, tuple[UUID, ...]]
    )
    membership_audits: dict[UUID, MembershipAuditRecord] = field(
        default_factory=dict[UUID, MembershipAuditRecord]
    )
    commit_count: int = 0
