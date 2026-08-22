"""Validation for integration identifiers."""

import re

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class IntegrationIdentifierValidator:
    """Validate reusable machine-integration identifier strings."""

    def validate(self, value: str, *, field_name: str) -> str:
        """Return a valid identifier or raise ``ValueError``."""
        if value != value.strip():
            raise ValueError(f"{field_name} must not contain surrounding whitespace")
        if not _IDENTIFIER_PATTERN.fullmatch(value):
            raise ValueError(
                f"{field_name} must be 1-128 characters and contain only letters, "
                "numbers, '.', '_', ':', or '-'"
            )
        return value
