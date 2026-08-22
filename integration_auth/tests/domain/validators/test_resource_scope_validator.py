"""Tests for resource and scope validation."""

import pytest

from integration_auth.domain.validators.resource_scope_validator import ResourceScopeValidator


def test_accepts_valid_resource_scope_pair() -> None:
    validator = ResourceScopeValidator()

    assert validator.validate("store", "store-123") == ("store", "store-123")


@pytest.mark.parametrize(
    ("resource_type", "resource_id"),
    [(" store", "store-123"), ("store", "store-123 ")],
)
def test_rejects_surrounding_whitespace(resource_type: str, resource_id: str) -> None:
    validator = ResourceScopeValidator()

    with pytest.raises(ValueError, match="surrounding whitespace"):
        validator.validate(resource_type, resource_id)


@pytest.mark.parametrize("resource_type", ["", "Store", "store.type", "x" * 65])
def test_rejects_invalid_resource_type(resource_type: str) -> None:
    validator = ResourceScopeValidator()

    with pytest.raises(ValueError, match="resource_type"):
        validator.validate(resource_type, "store-123")


@pytest.mark.parametrize("resource_id", ["", "store/123", "x" * 129])
def test_rejects_invalid_resource_id(resource_id: str) -> None:
    validator = ResourceScopeValidator()

    with pytest.raises(ValueError, match="resource_id"):
        validator.validate("store", resource_id)
