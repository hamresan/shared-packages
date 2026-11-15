import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class BusinessNameValidator:
    def validate(self, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Business name is required")
        if len(name) > 160:
            raise ValueError("Business name must be at most 160 characters")
        return name


class BranchNameValidator:
    def validate(self, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("Branch name is required")
        if len(name) > 160:
            raise ValueError("Branch name must be at most 160 characters")
        return name


class OptionalTextValidator:
    def validate(self, value: str | None, *, label: str, max_length: int) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        if len(normalized) > max_length:
            raise ValueError(f"{label} must be at most {max_length} characters")
        return normalized


class CountryCodeValidator:
    def validate(self, value: str) -> str:
        code = value.strip().upper()
        if re.fullmatch(r"[A-Z]{2}", code) is None:
            raise ValueError("Country code must contain exactly two ASCII letters")
        return code


class CurrencyCodeValidator:
    def validate(self, value: str) -> str:
        code = value.strip().upper()
        if re.fullmatch(r"[A-Z]{3}", code) is None:
            raise ValueError("Currency code must contain exactly three ASCII letters")
        return code


class LanguageCodeValidator:
    def validate(self, value: str) -> str:
        code = value.strip()
        if re.fullmatch(r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*", code) is None:
            raise ValueError("Language must be a valid basic language tag")
        return code.lower()


class BusinessTypeValidator:
    def validate(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if not normalized:
            return None
        if len(normalized) > 80:
            raise ValueError("Business type must be at most 80 characters")
        return normalized


class TimeZoneValidator:
    def validate(self, value: str) -> str:
        timezone = value.strip()
        if not timezone:
            raise ValueError("Timezone is required")
        try:
            ZoneInfo(timezone)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("Timezone must be a valid IANA timezone") from exc
        return timezone
