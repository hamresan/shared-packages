from enum import StrEnum


class BusinessStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class BranchStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class MembershipRole(StrEnum):
    OWNER = "owner"
    MEMBER = "member"


class MembershipStatus(StrEnum):
    INVITED = "invited"
    ACTIVE = "active"
    REVOKED = "revoked"


class BranchAccessScope(StrEnum):
    ALL = "all"
    SELECTED = "selected"
