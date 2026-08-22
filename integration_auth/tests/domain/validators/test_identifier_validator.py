"""Tests for integration identifier validation."""

import pytest

from integration_auth.domain.validators.identifier_validator import IntegrationIdentifierValidator


def test_accepts_valid_machine_identifier() -> None:
    validator = IntegrationIdentifierValidator()

    assert validator.validate("wp_store-123.v2", field_name="client_id") == "wp_store-123.v2"


@pytest.mark.parametrize("value", [" client", "client "])
def test_rejects_surrounding_whitespace(value: str) -> None:
    validator = IntegrationIdentifierValidator()

    with pytest.raises(ValueError, match="surrounding whitespace"):
        validator.validate(value, field_name="client_id")


@pytest.mark.parametrize("value", ["", "client/id", "x" * 129])
def test_rejects_invalid_identifier_format(value: str) -> None:
    validator = IntegrationIdentifierValidator()

    with pytest.raises(ValueError, match="1-128 characters"):
        validator.validate(value, field_name="credential_id")
