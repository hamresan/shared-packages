"""Normalized Instagram account types supported by the authorization package."""

from enum import StrEnum


class InstagramAccountType(StrEnum):
    """Normalized account types relevant to Instagram authorization eligibility."""

    BUSINESS = "business"
    CREATOR = "creator"


_ELIGIBLE_ACCOUNT_TYPES = frozenset(InstagramAccountType)


def is_eligible_account_type(account_type: InstagramAccountType | str) -> bool:
    """Return whether an account type is eligible for the initial package contract."""

    try:
        normalized = InstagramAccountType(account_type)
    except ValueError:
        return False
    return normalized in _ELIGIBLE_ACCOUNT_TYPES
