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
