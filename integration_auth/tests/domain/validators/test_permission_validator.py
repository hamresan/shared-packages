"""Tests for permission validation."""

import pytest

from integration_auth.domain.validators.permission_validator import PermissionValidator


def test_accepts_generic_dot_separated_permission() -> None:
    validator = PermissionValidator()

    assert validator.validate("catalog.product-read") == "catalog.product-read"


def test_rejects_surrounding_whitespace() -> None:
    validator = PermissionValidator()

    with pytest.raises(ValueError, match="surrounding whitespace"):
        validator.validate(" catalog.read")


@pytest.mark.parametrize("value", ["", "x" * 129])
def test_rejects_invalid_permission_length(value: str) -> None:
    validator = PermissionValidator()

    with pytest.raises(ValueError, match="1-128 characters"):
        validator.validate(value)


@pytest.mark.parametrize("value", ["Catalog.read", "catalog..read", "catalog.read/write"])
def test_rejects_invalid_permission_tokens(value: str) -> None:
    validator = PermissionValidator()

    with pytest.raises(ValueError, match="lowercase dot-separated tokens"):
        validator.validate(value)
