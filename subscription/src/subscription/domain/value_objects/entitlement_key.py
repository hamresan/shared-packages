import re
from dataclasses import dataclass

_ENTITLEMENT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*$")
_MAX_ENTITLEMENT_KEY_LENGTH = 128


@dataclass(frozen=True, slots=True)
class EntitlementKey:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > _MAX_ENTITLEMENT_KEY_LENGTH:
            raise ValueError(
                f"entitlement key must not exceed {_MAX_ENTITLEMENT_KEY_LENGTH} characters"
            )
        if not _ENTITLEMENT_KEY_PATTERN.fullmatch(self.value):
            raise ValueError(
                "entitlement key must be a canonical lowercase dotted identifier"
            )
