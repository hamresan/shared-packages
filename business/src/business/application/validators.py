from business.application.dto import CreateBusinessCommand, UpdateBusinessCommand
from business.domain.validators import (
    BusinessNameValidator,
    BusinessTypeValidator,
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageCodeValidator,
)


class BusinessProfileValidator:
    def __init__(
        self, name_validator: BusinessNameValidator, business_type_validator: BusinessTypeValidator
    ) -> None:
        self._name_validator = name_validator
        self._business_type_validator = business_type_validator

    def validate(self, *, name: str, business_type: str | None) -> tuple[str, str | None]:
        return (
            self._name_validator.validate(name),
            self._business_type_validator.validate(business_type),
        )


class CreateBusinessCommandValidator:
    def __init__(
        self,
        profile_validator: BusinessProfileValidator,
        country_validator: CountryCodeValidator,
        language_validator: LanguageCodeValidator,
        currency_validator: CurrencyCodeValidator,
    ) -> None:
        self._profile_validator = profile_validator
        self._country_validator = country_validator
        self._language_validator = language_validator
        self._currency_validator = currency_validator

    def validate(self, command: CreateBusinessCommand) -> CreateBusinessCommand:
        name, business_type = self._profile_validator.validate(
            name=command.name, business_type=command.business_type
        )
        return CreateBusinessCommand(
            name=name,
            business_type=business_type,
            country_code=self._country_validator.validate(command.country_code),
            default_language=self._language_validator.validate(command.default_language),
            default_currency_code=self._currency_validator.validate(command.default_currency_code),
        )


class UpdateBusinessCommandValidator:
    def __init__(self, profile_validator: BusinessProfileValidator) -> None:
        self._profile_validator = profile_validator

    def validate(self, command: UpdateBusinessCommand) -> UpdateBusinessCommand:
        name, business_type = self._profile_validator.validate(
            name=command.name, business_type=command.business_type
        )
        return UpdateBusinessCommand(
            business_id=command.business_id,
            name=name,
            business_type=business_type,
        )
