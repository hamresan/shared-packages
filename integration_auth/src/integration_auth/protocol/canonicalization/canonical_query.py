"""Deterministic canonical query encoding."""

from collections.abc import Iterable
from urllib.parse import quote


class CanonicalQueryEncoder:
    """Encode query pairs using RFC 3986 rules and deterministic sorting."""

    def encode(self, parameters: Iterable[tuple[str, str]]) -> str:
        encoded_pairs = [
            (
                quote(key, safe="-._~", encoding="utf-8", errors="strict"),
                quote(value, safe="-._~", encoding="utf-8", errors="strict"),
            )
            for key, value in parameters
        ]
        encoded_pairs.sort()
        return "&".join(f"{key}={value}" for key, value in encoded_pairs)
