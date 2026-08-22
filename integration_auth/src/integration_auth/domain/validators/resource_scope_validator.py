"""Validation shared by resource and scope value objects."""

import re

_RESOURCE_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
_RESOURCE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ResourceScopeValidator:
    """Validate generic resource type and identifier pairs."""

    def validate(self, resource_type: str, resource_id: str) -> tuple[str, str]:
        """Return a valid resource pair or raise ``ValueError``."""
        if resource_type != resource_type.strip() or resource_id != resource_id.strip():
            raise ValueError("resource values must not contain surrounding whitespace")
        if not _RESOURCE_TYPE_PATTERN.fullmatch(resource_type):
            raise ValueError(
                "resource_type must be 1-64 lowercase characters using letters, numbers, '_' or '-'"
            )
        if not _RESOURCE_ID_PATTERN.fullmatch(resource_id):
            raise ValueError(
                "resource_id must be 1-128 characters using letters, numbers, '.', '_' or '-'"
            )
        return resource_type, resource_id
