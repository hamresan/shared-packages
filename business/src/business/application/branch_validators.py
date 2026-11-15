from business.application.dto import CreateBranchCommand, ListBranchesQuery, UpdateBranchCommand
from business.domain.validators import (
    BranchNameValidator,
    CountryCodeValidator,
    OptionalTextValidator,
    TimeZoneValidator,
)
from business.domain.value_objects import BranchAddress, BranchContact


class BranchAddressValidator:
    def __init__(
        self, country_validator: CountryCodeValidator, text_validator: OptionalTextValidator
    ) -> None:
        self._country_validator = country_validator
        self._text_validator = text_validator

    def validate(self, address: BranchAddress | None) -> BranchAddress | None:
        if address is None:
            return None
        country = self._text_validator.validate(address.country_code, label="Country", max_length=2)
        normalized = BranchAddress(
            country_code=self._country_validator.validate(country) if country is not None else None,
            state_or_province=self._text_validator.validate(
                address.state_or_province, label="State", max_length=120
            ),
            city=self._text_validator.validate(address.city, label="City", max_length=120),
            area=self._text_validator.validate(address.area, label="Area", max_length=120),
            street=self._text_validator.validate(address.street, label="Street", max_length=200),
            building=self._text_validator.validate(
                address.building, label="Building", max_length=120
            ),
            postal_code=self._text_validator.validate(
                address.postal_code, label="Postal code", max_length=32
            ),
            additional_details=self._text_validator.validate(
                address.additional_details, label="Address details", max_length=500
            ),
        )
        return normalized if normalized != BranchAddress() else None


class BranchContactValidator:
    def __init__(self, text_validator: OptionalTextValidator) -> None:
        self._text_validator = text_validator

    def validate(self, contact: BranchContact | None) -> BranchContact | None:
        if contact is None:
            return None
        phone = self._text_validator.validate(contact.phone, label="Phone", max_length=50)
        email = self._text_validator.validate(contact.email, label="Email", max_length=254)
        if email is not None:
            parts = email.split("@")
            if len(parts) != 2 or not all(parts) or any(char.isspace() for char in email):
                raise ValueError("Email must be a valid contact address")
        if phone is None and email is None:
            return None
        return BranchContact(phone=phone, email=email)


class BranchDetailsValidator:
    def __init__(
        self,
        name_validator: BranchNameValidator,
        timezone_validator: TimeZoneValidator,
        address_validator: BranchAddressValidator,
        contact_validator: BranchContactValidator,
    ) -> None:
        self._name_validator = name_validator
        self._timezone_validator = timezone_validator
        self._address_validator = address_validator
        self._contact_validator = contact_validator

    def validate(
        self,
        *,
        name: str,
        timezone: str,
        address: BranchAddress | None,
        contact: BranchContact | None,
    ) -> tuple[str, str, BranchAddress | None, BranchContact | None]:
        return (
            self._name_validator.validate(name),
            self._timezone_validator.validate(timezone),
            self._address_validator.validate(address),
            self._contact_validator.validate(contact),
        )


class CreateBranchCommandValidator:
    def __init__(self, details_validator: BranchDetailsValidator) -> None:
        self._details_validator = details_validator

    def validate(self, command: CreateBranchCommand) -> CreateBranchCommand:
        name, timezone, address, contact = self._details_validator.validate(
            name=command.name,
            timezone=command.timezone,
            address=command.address,
            contact=command.contact,
        )
        return CreateBranchCommand(command.business_id, name, timezone, address, contact)


class UpdateBranchCommandValidator:
    def __init__(self, details_validator: BranchDetailsValidator) -> None:
        self._details_validator = details_validator

    def validate(self, command: UpdateBranchCommand) -> UpdateBranchCommand:
        name, timezone, address, contact = self._details_validator.validate(
            name=command.name,
            timezone=command.timezone,
            address=command.address,
            contact=command.contact,
        )
        return UpdateBranchCommand(
            command.business_id, command.branch_id, name, timezone, address, contact
        )


class ListBranchesQueryValidator:
    def __init__(
        self, country_validator: CountryCodeValidator, text_validator: OptionalTextValidator
    ) -> None:
        self._country_validator = country_validator
        self._text_validator = text_validator

    def validate(self, query: ListBranchesQuery) -> ListBranchesQuery:
        city = self._text_validator.validate(query.city, label="City", max_length=120)
        country = self._text_validator.validate(query.country_code, label="Country", max_length=2)
        return ListBranchesQuery(
            business_id=query.business_id,
            city=city.casefold() if city is not None else None,
            country_code=self._country_validator.validate(country) if country is not None else None,
        )
