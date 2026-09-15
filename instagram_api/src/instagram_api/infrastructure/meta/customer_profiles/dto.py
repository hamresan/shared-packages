"""Provider DTO for Meta Instagram customer profile data."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramCustomerProfileDto:
    """Typed Meta customer profile payload."""

    user_id: str
    username: str | None
    name: str | None
    profile_picture_url: str | None
