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


def test_boolean_entitlement_value_reports_boolean_type() -> None:
    value = BooleanEntitlementValue(True)

    assert value.value is True
    assert value.value_type is EntitlementValueType.BOOLEAN


def test_integer_entitlement_value_reports_integer_type() -> None:
    value = IntegerEntitlementValue(50)

    assert value.value == 50
    assert value.value_type is EntitlementValueType.INTEGER


def test_integer_entitlement_value_rejects_bool() -> None:
    with pytest.raises(TypeError, match="not bool"):
        IntegerEntitlementValue(True)


def test_decimal_entitlement_value_reports_decimal_type() -> None:
    value = DecimalEntitlementValue(Decimal("12.5"))

    assert value.value == Decimal("12.5")
    assert value.value_type is EntitlementValueType.DECIMAL


@pytest.mark.parametrize("raw_value", [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")])
def test_decimal_entitlement_value_requires_finite_value(raw_value: Decimal) -> None:
    with pytest.raises(ValueError, match="finite"):
        DecimalEntitlementValue(raw_value)


def test_string_entitlement_value_reports_string_type() -> None:
    value = StringEntitlementValue("premium")

    assert value.value == "premium"
    assert value.value_type is EntitlementValueType.STRING


def test_unlimited_entitlement_value_reports_unlimited_type() -> None:
    value = UnlimitedEntitlementValue()

    assert value.value_type is EntitlementValueType.UNLIMITED
