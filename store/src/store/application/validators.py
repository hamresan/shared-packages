from store.application.dto import CreateStoreCommand
from store.domain import (
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageSettingsValidator,
    StoreNameValidator,
)


class CreateStoreCommandValidator:
    def __init__(
        self,
        name_validator: StoreNameValidator,
        language_validator: LanguageSettingsValidator,
        country_validator: CountryCodeValidator,
        currency_validator: CurrencyCodeValidator,
    ) -> None:
        self._name_validator = name_validator
        self._language_validator = language_validator
        self._country_validator = country_validator
        self._currency_validator = currency_validator

    def validate(self, command: CreateStoreCommand) -> CreateStoreCommand:
        name = self._name_validator.validate(command.name)
        primary_language, _ = self._language_validator.validate(
            primary_language=command.primary_language,
            supported_languages=(command.primary_language,),
        )
        country_code = self._country_validator.validate(command.country_code)
        base_currency_code = self._currency_validator.validate(command.base_currency_code)
        business_type = command.business_type.strip().lower()
        if not business_type:
            raise ValueError("Business type is required")
        return CreateStoreCommand(
            owner_user_id=command.owner_user_id,
            name=name,
            business_type=business_type,
            primary_language=primary_language,
            country_code=country_code,
            base_currency_code=base_currency_code,
        )
