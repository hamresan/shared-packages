from decimal import Decimal

from subscription.domain import (
    BooleanEntitlementValue,
    DecimalEntitlementValue,
    EntitlementValue,
    EntitlementValueType,
    IntegerEntitlementValue,
    StringEntitlementValue,
    UnlimitedEntitlementValue,
)
from subscription.presentation.schemas.common import EntitlementValueSchema


class EntitlementValuePresentationMapper:
    def from_schema(self, schema: EntitlementValueSchema) -> EntitlementValue:
        value_type = schema.value_type
        value = schema.value
        if value_type is EntitlementValueType.BOOLEAN:
            if type(value) is not bool:
                raise ValueError("boolean entitlement requires a boolean value")
            return BooleanEntitlementValue(value)
        if value_type is EntitlementValueType.INTEGER:
            if type(value) is not int:
                raise ValueError("integer entitlement requires an integer value")
            return IntegerEntitlementValue(value)
        if value_type is EntitlementValueType.DECIMAL:
            if value is None or isinstance(value, bool):
                raise ValueError("decimal entitlement requires a numeric value")
            return DecimalEntitlementValue(Decimal(str(value)))
        if value_type is EntitlementValueType.STRING:
            if not isinstance(value, str):
                raise ValueError("string entitlement requires a string value")
            return StringEntitlementValue(value)
        if value is not None:
            raise ValueError("unlimited entitlement must not contain a value")
        return UnlimitedEntitlementValue()

    def to_schema(self, value: EntitlementValue) -> EntitlementValueSchema:
        if isinstance(value, UnlimitedEntitlementValue):
            return EntitlementValueSchema(value_type=value.value_type, value=None)
        return EntitlementValueSchema(value_type=value.value_type, value=value.value)
