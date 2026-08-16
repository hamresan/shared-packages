from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class StoreNameValidator:
    def validate(self, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Store name is required")
        if len(normalized) > 160:
            raise ValueError("Store name must be at most 160 characters")
        return normalized


class LanguageSettingsValidator:
    def validate(
        self,
        *,
        primary_language: str,
        supported_languages: tuple[str, ...],
    ) -> tuple[str, tuple[str, ...]]:
        primary = primary_language.strip().lower()
        languages = tuple(language.strip().lower() for language in supported_languages)
        if not primary:
            raise ValueError("Primary language is required")
        if any(not language for language in languages):
            raise ValueError("Supported languages cannot contain blank values")
        if len(set(languages)) != len(languages):
            raise ValueError("Supported languages must be unique")
        if primary not in languages:
            raise ValueError("Primary language must be included in supported languages")
        return primary, languages


class CountryCodeValidator:
    def validate(self, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 2 or not normalized.isalpha():
            raise ValueError("Country code must be a two-letter code")
        return normalized


class CurrencyCodeValidator:
    def validate(self, value: str) -> str:
        normalized = value.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise ValueError("Currency code must be a three-letter code")
        return normalized


class TimeZoneValidator:
    def validate(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        try:
            ZoneInfo(normalized)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Timezone must be a valid IANA timezone") from exc
        return normalized
