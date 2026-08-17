import pytest

from store.domain import (
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageSettingsValidator,
    StoreNameValidator,
    TimeZoneValidator,
)


def test_store_name_validator_normalizes_name() -> None:
    assert StoreNameValidator().validate("  My Store  ") == "My Store"


def test_language_settings_validator_normalizes_values() -> None:
    primary, supported = LanguageSettingsValidator().validate(
        primary_language="EN",
        supported_languages=("EN", "fa"),
    )

    assert primary == "en"
    assert supported == ("en", "fa")


def test_language_settings_validator_rejects_primary_outside_supported() -> None:
    with pytest.raises(ValueError):
        LanguageSettingsValidator().validate(
            primary_language="en",
            supported_languages=("fa",),
        )


def test_country_and_currency_validators_normalize_codes() -> None:
    assert CountryCodeValidator().validate("om") == "OM"
    assert CurrencyCodeValidator().validate("omr") == "OMR"


def test_timezone_validator_accepts_iana_timezone() -> None:
    assert TimeZoneValidator().validate("Asia/Muscat") == "Asia/Muscat"


def test_timezone_validator_rejects_unknown_timezone() -> None:
    with pytest.raises(ValueError):
        TimeZoneValidator().validate("Mars/Olympus")
