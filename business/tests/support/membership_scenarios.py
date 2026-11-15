from uuid import UUID

from business.application.actor import AuthenticatedActor
from business.domain.enums import BranchAccessScope, MembershipRole, MembershipStatus
from tests.support.builders import (
    OTHER_USER_ID,
    TEST_TIME,
    TEST_USER_ID,
    build_membership,
)
from tests.support.fakes.clock import FixedClock
from tests.support.fakes.database import InMemoryBusinessDatabase
from tests.support.fakes.identifiers import SequentialIdentifierGenerator
from tests.support.scenarios import seed_owned_business

MEMBER_ID = UUID("314b0ef4-52f1-4fbd-8435-7461800a8f31")
AUDIT_ID = UUID("65e24f6d-ae99-474a-bb2c-491f9fd5c2dd")
OTHER_BRANCH_ID = UUID("f88808d2-b6f9-42f6-acbe-c463f94c85c1")
FOREIGN_BUSINESS_ID = UUID("3af3e7c4-57bb-42e5-bb9b-62bde0218f3a")


def seed_member(
    database: InMemoryBusinessDatabase,
    *,
    status: MembershipStatus = MembershipStatus.ACTIVE,
    role: MembershipRole = MembershipRole.MEMBER,
    scope: BranchAccessScope = BranchAccessScope.SELECTED,
) -> None:
    database.memberships[MEMBER_ID] = build_membership(
        membership_id=MEMBER_ID,
        user_id=OTHER_USER_ID,
        status=status,
        role=role,
        branch_access_scope=scope,
    )


def setup_membership_database(*, include_member: bool = True) -> InMemoryBusinessDatabase:
    database = InMemoryBusinessDatabase()
    seed_owned_business(database)
    if include_member:
        seed_member(database)
    return database


def owner_actor() -> AuthenticatedActor:
    return AuthenticatedActor(TEST_USER_ID)


def member_actor() -> AuthenticatedActor:
    return AuthenticatedActor(OTHER_USER_ID)


def clock() -> FixedClock:
    return FixedClock(TEST_TIME)


def ids(*values: UUID) -> SequentialIdentifierGenerator:
    return SequentialIdentifierGenerator(values)
