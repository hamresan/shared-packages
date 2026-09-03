"""Meta Instagram identity DTO."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramIdentityDto:
    """Validated provider identity payload before domain mapping."""

    user_id: str
    username: str
    account_type: str
