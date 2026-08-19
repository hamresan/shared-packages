import re
import unicodedata

from identity.application.contracts.security import IdentityNormalizer
from identity.application.errors import InvalidIdentityValueError
from identity.domain import IdentityType

_E164_PATTERN = re.compile(r"^\+[1-9][0-9]{6,14}$")
_MOBILE_SEPARATORS = re.compile(r"[\s().-]+")


class DefaultIdentityNormalizer(IdentityNormalizer):
    def normalize(self, identity_type: IdentityType, value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).strip()
        if identity_type is IdentityType.EMAIL:
            return self._normalize_email(normalized)
        if identity_type is IdentityType.MOBILE:
            return self._normalize_mobile(normalized)
        return normalized

    def _normalize_email(self, value: str) -> str:
        normalized = value.casefold()
        if any(character.isspace() or unicodedata.category(character).startswith("C") for character in normalized):
            raise InvalidIdentityValueError("Email contains invalid whitespace or control characters")
        local_part, separator, domain = normalized.rpartition("@")
        if not separator or not local_part or not domain or "@" in local_part:
            raise InvalidIdentityValueError("Email format is invalid")
        return normalized

    def _normalize_mobile(self, value: str) -> str:
        normalized = self._normalize_unicode_digits(value)
        normalized = _MOBILE_SEPARATORS.sub("", normalized)
        if normalized.startswith("00"):
            normalized = f"+{normalized[2:]}"
        if not _E164_PATTERN.fullmatch(normalized):
            raise InvalidIdentityValueError(
                "Mobile number must use international E.164 format"
            )
        return normalized

    def _normalize_unicode_digits(self, value: str) -> str:
        characters: list[str] = []
        for character in value:
            if character.isdecimal():
                characters.append(str(unicodedata.decimal(character)))
            else:
                characters.append(character)
        return "".join(characters)
