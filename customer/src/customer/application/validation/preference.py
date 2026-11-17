import re

from customer.domain.errors import CustomerValidationError
from customer.domain.preference import PreferenceValue


class PreferenceValidator:
    def normalize_key(self, key: str) -> str:
        candidate = key.strip().lower()
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{0,79}", candidate):
            raise CustomerValidationError("Invalid preference key")
        return candidate

    def validate(self, key: str, value: PreferenceValue) -> str:
        candidate = self.normalize_key(key)
        if type(value) not in (str, bool, int):
            raise CustomerValidationError("Unsupported preference value type")
        if isinstance(value, str) and len(value) > 500:
            raise CustomerValidationError("Preference value is too long")
        return candidate
