"""Tests for IntegrationScope."""

import pytest

from integration_auth.domain.value_objects.integration_scope import IntegrationScope


def test_scope_exposes_canonical_value() -> None:
    scope = IntegrationScope(resource_type="store", resource_id="store-123")

    assert scope.value == "store:store-123"
    assert str(scope) == "store:store-123"


def test_scope_can_be_created_from_canonical_value() -> None:
    scope = IntegrationScope.from_value("organization:org-42")

    assert scope == IntegrationScope(resource_type="organization", resource_id="org-42")


@pytest.mark.parametrize("value", ["store", "store:one:two", ":store-123"])
def test_scope_rejects_invalid_canonical_value(value: str) -> None:
    with pytest.raises(ValueError):
        IntegrationScope.from_value(value)
