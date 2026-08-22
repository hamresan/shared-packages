"""Validation for canonical request protocol values."""

import re

_HTTP_METHOD_PATTERN = re.compile(r"^[A-Z]+$")
_NONCE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CanonicalRequestValidator:
    """Validate values that participate in the signed canonical request."""

    def validate(
        self,
        *,
        method: str,
        path: str,
        canonical_query: str,
        timestamp: int,
        nonce: str,
        body_sha256: str,
    ) -> None:
        if not _HTTP_METHOD_PATTERN.fullmatch(method):
            raise ValueError("method must be a non-empty uppercase HTTP token")
        if not path.startswith("/") or "?" in path or "#" in path or "\n" in path or "\r" in path:
            raise ValueError(
                "path must be an origin-form path without query, fragment, or newlines"
            )
        if (
            "?" in canonical_query
            or "#" in canonical_query
            or "\n" in canonical_query
            or "\r" in canonical_query
        ):
            raise ValueError("canonical_query must not include '?', fragment, or newlines")
        if timestamp < 0:
            raise ValueError("timestamp must be non-negative")
        if not _NONCE_PATTERN.fullmatch(nonce):
            raise ValueError("nonce must be 1-128 safe characters")
        if not _SHA256_HEX_PATTERN.fullmatch(body_sha256):
            raise ValueError("body_sha256 must be a lowercase 64-character hexadecimal digest")
