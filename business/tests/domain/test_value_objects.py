from dataclasses import FrozenInstanceError

import pytest

from business.domain import BranchAddress, BranchContact


def test_branch_address_can_contain_only_a_city() -> None:
    address = BranchAddress(city="Muscat")

    assert address.city == "Muscat"
    assert address.street is None
    assert address.country_code is None


def test_branch_address_can_hold_a_multinational_location() -> None:
    address = BranchAddress(country_code="AE", state_or_province="Dubai", city="Dubai")

    assert address.country_code == "AE"
    assert address.state_or_province == "Dubai"


def test_branch_address_is_immutable() -> None:
    address = BranchAddress(city="Muscat")

    with pytest.raises(FrozenInstanceError):
        address.__setattr__("city", "Salalah")


def test_branch_contact_is_immutable_and_optional() -> None:
    contact = BranchContact(email="example@example.com")

    assert contact.phone is None
    assert contact.email == "example@example.com"
    with pytest.raises(FrozenInstanceError):
        contact.__setattr__("phone", "+96899999999")
