import pytest

from business.application.dto import CreateBusinessCommand, UpdateBusinessCommand
from business.application.validators import UpdateBusinessCommandValidator
from tests.support.builders import TEST_BUSINESS_ID
from tests.support.factories import build_create_validator, build_profile_validator


def test_create_command_validator_normalizes_profile_and_settings() -> None:
    command = CreateBusinessCommand(
        name="  Muscat Bakery  ",
        business_type="  BAKERY  ",
        country_code="om",
        default_language="EN-OM",
        default_currency_code="omr",
    )

    validated = build_create_validator().validate(command)

    assert validated.name == "Muscat Bakery"
    assert validated.business_type == "bakery"
    assert validated.country_code == "OM"
    assert validated.default_language == "en-om"
    assert validated.default_currency_code == "OMR"
    assert command.name == "  Muscat Bakery  "


@pytest.mark.parametrize(
    "command",
    [
        CreateBusinessCommand("", "OM", "en", "OMR"),
        CreateBusinessCommand("Name", "OMN", "en", "OMR"),
        CreateBusinessCommand("Name", "OM", "x", "OMR"),
        CreateBusinessCommand("Name", "OM", "en", "OMRR"),
    ],
)
def test_create_command_validator_rejects_invalid_inputs(command: CreateBusinessCommand) -> None:
    with pytest.raises(ValueError):
        build_create_validator().validate(command)


def test_profile_validator_can_normalize_an_optional_business_type() -> None:
    assert build_profile_validator().validate(name="  Name  ", business_type=" ") == (
        "Name",
        None,
    )


def test_update_command_preserves_business_identifier() -> None:
    command = UpdateBusinessCommand(TEST_BUSINESS_ID, "  New Name  ", " SALON ")

    validated = UpdateBusinessCommandValidator(build_profile_validator()).validate(command)

    assert validated.business_id == TEST_BUSINESS_ID
    assert validated.name == "New Name"
    assert validated.business_type == "salon"
