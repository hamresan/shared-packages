from datetime import datetime
from uuid import UUID

from business.application.contracts import IdentifierGenerator
from business.domain.enums import MembershipRole, MembershipStatus
from business.domain.membership import BusinessMembership


class OwnerMembershipFactory:
    def __init__(self, identifier_generator: IdentifierGenerator) -> None:
        self._identifier_generator = identifier_generator

    def create(
        self, *, business_id: UUID, user_id: UUID, created_at: datetime
    ) -> BusinessMembership:
        return BusinessMembership(
            id=self._identifier_generator.new_id(),
            business_id=business_id,
            user_id=user_id,
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
            created_at=created_at,
            updated_at=created_at,
        )
