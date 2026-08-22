"""Validation for required integration authentication headers."""

from fastapi import Request


class InvalidSignedRequestHeadersError(ValueError):
    """Raised when required integration authentication headers are missing or invalid."""


class RequiredHeaderReader:
    """Read one required HTTP header and reject blank values."""

    def read(self, request: Request, name: str) -> str:
        value = request.headers.get(name)
        if value is None or not value.strip():
            raise InvalidSignedRequestHeadersError("missing integration authentication header")
        return value.strip()
