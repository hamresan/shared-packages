"""Tests for integration identifier value objects."""

import pytest

from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


def test_client_id_preserves_valid_value() -> None:
    client_id = IntegrationClientId("client_123")

    assert client_id.value == "client_123"
    assert str(client_id) == "client_123"


def test_credential_id_preserves_valid_value() -> None:
    credential_id = IntegrationCredentialId("cred-123")

    assert credential_id.value == "cred-123"
    assert str(credential_id) == "cred-123"


@pytest.mark.parametrize(
    ("factory", "value"),
    [(IntegrationClientId, "bad id"), (IntegrationCredentialId, "")],
)
def test_identifiers_reject_invalid_values(factory: type[object], value: str) -> None:
    with pytest.raises(ValueError):
        factory(value)
