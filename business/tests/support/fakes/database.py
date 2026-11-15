from dataclasses import dataclass, field
from uuid import UUID

from business.domain.business import Business
from business.domain.membership import BusinessMembership


@dataclass(slots=True)
class InMemoryBusinessDatabase:
    businesses: dict[UUID, Business] = field(default_factory=dict[UUID, Business])
    memberships: dict[UUID, BusinessMembership] = field(
        default_factory=dict[UUID, BusinessMembership]
    )
    commit_count: int = 0
