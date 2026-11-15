from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BranchAddress:
    """Optional physical location details; a city alone is a valid address."""

    country_code: str | None = None
    state_or_province: str | None = None
    city: str | None = None
    area: str | None = None
    street: str | None = None
    building: str | None = None
    postal_code: str | None = None
    additional_details: str | None = None
