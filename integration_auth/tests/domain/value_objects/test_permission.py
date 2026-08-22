"""Tests for Permission."""

import pytest

from integration_auth.domain.value_objects.permission import Permission


def test_permission_is_immutable_value_object() -> None:
    permission = Permission("orders.read")

    assert permission.value == "orders.read"
    assert str(permission) == "orders.read"
    assert permission == Permission("orders.read")


def test_permission_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        Permission("Orders.Read")
