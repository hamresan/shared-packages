"""Typed response parsing helpers for FastAPI adapter tests."""

from typing import cast

from httpx import Response


def response_json_object(response: Response) -> dict[str, object]:
    """Return a JSON object with an explicit test-facing type."""
    return cast(dict[str, object], response.json())


def response_json_object_list(response: Response) -> list[dict[str, object]]:
    """Return a JSON object list with an explicit test-facing type."""
    return cast(list[dict[str, object]], response.json())


def response_json_string(response: Response, key: str) -> str:
    """Read one required string field from a JSON object response."""
    value = response_json_object(response)[key]
    if not isinstance(value, str):
        raise AssertionError(f"Expected response field {key!r} to be a string")
    return value
