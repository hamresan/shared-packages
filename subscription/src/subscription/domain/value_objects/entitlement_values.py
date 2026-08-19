from dataclasses import dataclass
from decimal import Decimal

from subscription.domain.enums.entitlement import EntitlementValueType


@dataclass(frozen=True, slots=True)
class BooleanEntitlementValue:
    value: bool

    @property
    def value_type(self) -> EntitlementValueType:
        return EntitlementValueType.BOOLEAN


@dataclass(frozen=True, slots=True)
class IntegerEntitlementValue:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool):
            raise TypeError("integer entitlement value must be an int, not bool")

    @property
    def value_type(self) -> EntitlementValueType:
        return EntitlementValueType.INTEGER


@dataclass(frozen=True, slots=True)
class DecimalEntitlementValue:
    value: Decimal

    def __post_init__(self) -> None:
        if not self.value.is_finite():
            raise ValueError("decimal entitlement value must be finite")

    @property
    def value_type(self) -> EntitlementValueType:
        return EntitlementValueType.DECIMAL


@dataclass(frozen=True, slots=True)
class StringEntitlementValue:
    value: str

    @property
    def value_type(self) -> EntitlementValueType:
        return EntitlementValueType.STRING


@dataclass(frozen=True, slots=True)
class UnlimitedEntitlementValue:
    @property
    def value_type(self) -> EntitlementValueType:
        return EntitlementValueType.UNLIMITED


type EntitlementValue = (
    BooleanEntitlementValue
    | IntegerEntitlementValue
    | DecimalEntitlementValue
    | StringEntitlementValue
    | UnlimitedEntitlementValue
)
