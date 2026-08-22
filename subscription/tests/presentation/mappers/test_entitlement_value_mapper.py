from decimal import Decimal

import pytest

from subscription import (
    BooleanEntitlementValue,
    DecimalEntitlementValue,
    EntitlementValueType,
    IntegerEntitlementValue,
    StringEntitlementValue,
    UnlimitedEntitlementValue,
)
from subscription.presentation.mappers import EntitlementValuePresentationMapper
from subscription.presentation.schemas import EntitlementValueSchema


@pytest.mark.parametrize(
    ("schema", "expected"),
    [
        (
            EntitlementValueSchema(value_type=EntitlementValueType.BOOLEAN, value=True),
            BooleanEntitlementValue(True),
        ),
        (
            EntitlementValueSchema(value_type=EntitlementValueType.INTEGER, value=5),
            IntegerEntitlementValue(5),
        ),
        (
            EntitlementValueSchema(value_type=EntitlementValueType.DECIMAL, value=Decimal("1.5")),
            DecimalEntitlementValue(Decimal("1.5")),
        ),
        (
            EntitlementValueSchema(value_type=EntitlementValueType.STRING, value="gpt-x"),
            StringEntitlementValue("gpt-x"),
        ),
        (
            EntitlementValueSchema(value_type=EntitlementValueType.UNLIMITED, value=None),
            UnlimitedEntitlementValue(),
        ),
    ],
)
def test_entitlement_value_mapper_maps_supported_values(
    schema: EntitlementValueSchema,
    expected: object,
) -> None:
    mapper = EntitlementValuePresentationMapper()

    assert mapper.from_schema(schema) == expected


def test_entitlement_value_mapper_rejects_mismatched_value() -> None:
    mapper = EntitlementValuePresentationMapper()
    schema = EntitlementValueSchema(value_type=EntitlementValueType.BOOLEAN, value="true")

    with pytest.raises(ValueError):
        mapper.from_schema(schema)


def test_entitlement_value_mapper_serializes_unlimited_without_payload() -> None:
    mapper = EntitlementValuePresentationMapper()

    result = mapper.to_schema(UnlimitedEntitlementValue())

    assert result.value_type is EntitlementValueType.UNLIMITED
    assert result.value is None
