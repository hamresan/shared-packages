"""Validation for integration permission values."""

import re

_PERMISSION_SEGMENT_PATTERN = re.compile(r"^[a-z][a-z0-9_-]*$")


class PermissionValidator:
    """Validate generic permission names such as ``catalog.read``."""

    def validate(self, value: str) -> str:
        """Return a valid permission or raise ``ValueError``."""
        if value != value.strip():
            raise ValueError("permission must not contain surrounding whitespace")
        if not value or len(value) > 128:
            raise ValueError("permission must contain 1-128 characters")

        segments = value.split(".")
        if any(not _PERMISSION_SEGMENT_PATTERN.fullmatch(segment) for segment in segments):
            raise ValueError(
                "permission must contain lowercase dot-separated tokens using letters, "
                "numbers, '_' or '-'"
            )
        return value
