import re

from identity.application.contracts.security import IdentityNormalizer
from identity.domain import IdentityType


class DefaultIdentityNormalizer(IdentityNormalizer):
    def normalize(self, identity_type: IdentityType, value: str) -> str:
        normalized = value.strip()
        if identity_type is IdentityType.EMAIL:
            return normalized.casefold()
        if identity_type is IdentityType.MOBILE:
            return re.sub(r"[\s()-]", "", normalized)
        return normalized
