import re
import unicodedata

from identity.application.contracts.security import IdentityNormalizer
from identity.application.errors import InvalidIdentityValueError
from identity.domain import IdentityType

_E164_PATTERN = re.compile(r"^\+[1-9][0-9]{6,14}$")
_MOBILE_SEPARATORS = re.compile(r"[\s().-]+")


class EmailIdentityNormalizer:
    def normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).strip().casefold()
        if any(
            character.isspace() or unicodedata.category(character).startswith("C")
            for character in normalized
        ):
            raise InvalidIdentityValueError(
                "Email contains invalid whitespace or control characters"
            )
        local_part, separator, domain = normalized.rpartition("@")
        if not separator or not local_part or not domain or "@" in local_part:
            raise InvalidIdentityValueError("Email format is invalid")
        return normalized


class MobileIdentityNormalizer:
    def normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).strip()
        characters: list[str] = []
        for character in normalized:
            if character.isdecimal():
                characters.append(str(unicodedata.decimal(character)))
            else:
                characters.append(character)
        normalized = _MOBILE_SEPARATORS.sub("", "".join(characters))
        if normalized.startswith("00"):
            normalized = f"+{normalized[2:]}"
        if not _E164_PATTERN.fullmatch(normalized):
            raise InvalidIdentityValueError("Mobile number must use international E.164 format")
        return normalized


class DefaultIdentityNormalizer(IdentityNormalizer):
    def __init__(
        self,
        email_normalizer: EmailIdentityNormalizer | None = None,
        mobile_normalizer: MobileIdentityNormalizer | None = None,
    ) -> None:
        self._email_normalizer = email_normalizer or EmailIdentityNormalizer()
        self._mobile_normalizer = mobile_normalizer or MobileIdentityNormalizer()

    def normalize(self, identity_type: IdentityType, value: str) -> str:
        if identity_type is IdentityType.EMAIL:
            return self._email_normalizer.normalize(value)
        if identity_type is IdentityType.MOBILE:
            return self._mobile_normalizer.normalize(value)
        return unicodedata.normalize("NFKC", value).strip()
