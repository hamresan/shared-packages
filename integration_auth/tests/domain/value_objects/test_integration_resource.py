"""Tests for IntegrationResource."""

import pytest

from integration_auth.domain.value_objects.integration_resource import IntegrationResource


def test_resource_exposes_matching_scope_value() -> None:
    resource = IntegrationResource(resource_type="store", resource_id="store-123")

    assert resource.scope_value == "store:store-123"


def test_resource_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="resource_type"):
        IntegrationResource(resource_type="Store", resource_id="store-123")
