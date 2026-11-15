import pytest

from business.application.branch_validators import (
    BranchAddressValidator,
    BranchContactValidator,
    CreateBranchCommandValidator,
    ListBranchesQueryValidator,
    UpdateBranchCommandValidator,
)
from business.application.dto import CreateBranchCommand, ListBranchesQuery, UpdateBranchCommand
from business.domain import (
    BranchAddress,
    BranchContact,
    CountryCodeValidator,
    OptionalTextValidator,
)
from tests.support.builders import TEST_BRANCH_ID, TEST_BUSINESS_ID
from tests.support.factories import build_branch_details_validator


def test_create_branch_normalizes_name_timezone_address_and_contact() -> None:
    command = CreateBranchCommand(
        business_id=TEST_BUSINESS_ID,
        name="  Main Branch  ",
        timezone=" Asia/Muscat ",
        address=BranchAddress(city=" Muscat ", country_code="om", street=" Sultan Qaboos "),
        contact=BranchContact(phone=" +96812345678 ", email=" hello@example.com "),
    )

    validated = CreateBranchCommandValidator(build_branch_details_validator()).validate(command)

    assert validated.business_id == TEST_BUSINESS_ID
    assert validated.name == "Main Branch"
    assert validated.timezone == "Asia/Muscat"
    assert validated.address == BranchAddress(
        city="Muscat", country_code="OM", street="Sultan Qaboos"
    )
    assert validated.contact == BranchContact(phone="+96812345678", email="hello@example.com")
    assert command.address is not None and command.address.city == " Muscat "


def test_branch_can_be_created_without_physical_address_or_contact() -> None:
    command = CreateBranchCommand(TEST_BUSINESS_ID, "Remote Unit", "UTC")

    validated = CreateBranchCommandValidator(build_branch_details_validator()).validate(command)

    assert validated.address is None
    assert validated.contact is None


def test_address_with_city_only_is_valid() -> None:
    validator = BranchAddressValidator(CountryCodeValidator(), OptionalTextValidator())

    assert validator.validate(BranchAddress(city="  Salalah  ")) == BranchAddress(city="Salalah")


def test_empty_address_is_reduced_to_none() -> None:
    validator = BranchAddressValidator(CountryCodeValidator(), OptionalTextValidator())

    assert validator.validate(None) is None
    assert validator.validate(BranchAddress(city=" ", street=" ")) is None


@pytest.mark.parametrize(
    "address",
    [BranchAddress(country_code="OMN"), BranchAddress(city="x" * 121)],
)
def test_invalid_address_fields_are_rejected(address: BranchAddress) -> None:
    validator = BranchAddressValidator(CountryCodeValidator(), OptionalTextValidator())

    with pytest.raises(ValueError):
        validator.validate(address)


def test_contact_with_only_email_is_valid() -> None:
    validator = BranchContactValidator(OptionalTextValidator())

    assert validator.validate(BranchContact(email="contact@example.com")) == BranchContact(
        email="contact@example.com"
    )
    assert validator.validate(None) is None
    assert validator.validate(BranchContact(phone="  ", email=" ")) is None


@pytest.mark.parametrize(
    "email", ["invalid", "@example.com", "person@", "a@@example.com", "a b@example.com"]
)
def test_contact_rejects_malformed_email(email: str) -> None:
    with pytest.raises(ValueError, match="Email"):
        BranchContactValidator(OptionalTextValidator()).validate(BranchContact(email=email))


def test_contact_rejects_overlong_phone() -> None:
    with pytest.raises(ValueError, match="Phone"):
        BranchContactValidator(OptionalTextValidator()).validate(BranchContact(phone="1" * 51))


@pytest.mark.parametrize("name, timezone", [(" ", "UTC"), ("Name", "Mars/Unknown")])
def test_create_branch_rejects_invalid_name_or_timezone(name: str, timezone: str) -> None:
    command = CreateBranchCommand(TEST_BUSINESS_ID, name, timezone)

    with pytest.raises(ValueError):
        CreateBranchCommandValidator(build_branch_details_validator()).validate(command)


def test_update_branch_preserves_both_immutable_identifiers() -> None:
    command = UpdateBranchCommand(
        TEST_BUSINESS_ID,
        TEST_BRANCH_ID,
        " Updated ",
        "UTC",
        BranchAddress(city="  Muscat  "),
        None,
    )

    validated = UpdateBranchCommandValidator(build_branch_details_validator()).validate(command)

    assert validated.business_id == TEST_BUSINESS_ID
    assert validated.branch_id == TEST_BRANCH_ID
    assert validated.name == "Updated"
    assert validated.address == BranchAddress(city="Muscat")


def test_branch_search_normalizes_case_and_country_filter() -> None:
    validator = ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator())

    validated = validator.validate(ListBranchesQuery(TEST_BUSINESS_ID, " MuSCat ", "om"))

    assert validated.city == "muscat"
    assert validated.country_code == "OM"
    assert validated.business_id == TEST_BUSINESS_ID


def test_branch_search_accepts_no_filters_or_blank_filters() -> None:
    validator = ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator())

    assert validator.validate(ListBranchesQuery(TEST_BUSINESS_ID)) == ListBranchesQuery(
        TEST_BUSINESS_ID
    )
    assert validator.validate(ListBranchesQuery(TEST_BUSINESS_ID, " ", " ")) == ListBranchesQuery(
        TEST_BUSINESS_ID
    )


def test_branch_search_rejects_invalid_country_code() -> None:
    validator = ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator())

    with pytest.raises(ValueError):
        validator.validate(ListBranchesQuery(TEST_BUSINESS_ID, country_code="USA"))
