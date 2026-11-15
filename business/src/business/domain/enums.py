from enum import StrEnum


class BusinessStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class BranchStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class MembershipRole(StrEnum):
    OWNER = "owner"
    MANAGER = "manager"
    MEMBER = "member"


class MembershipStatus(StrEnum):
    INVITED = "invited"
    ACTIVE = "active"
    REVOKED = "revoked"


class BranchAccessScope(StrEnum):
    ALL = "all"
    SELECTED = "selected"


class MembershipAuditAction(StrEnum):
    INVITED = "invited"
    ACCEPTED = "accepted"
    ROLE_CHANGED = "role_changed"
    REVOKED = "revoked"
    BRANCH_ACCESS_CHANGED = "branch_access_changed"
    OWNERSHIP_TRANSFERRED = "ownership_transferred"
