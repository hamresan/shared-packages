"""Typed response parsing helpers for FastAPI adapter tests."""

from typing import Protocol, cast


class JsonResponse(Protocol):
    """Minimal response contract required by JSON parsing test helpers."""

    def json(self) -> object:
        """Return the decoded response payload."""
        ...


def response_json_object(response: JsonResponse) -> dict[str, object]:
    """Return a JSON object with an explicit test-facing type."""
    payload = response.json()
    if not isinstance(payload, dict):
        raise AssertionError("Expected response JSON payload to be an object")
    return cast(dict[str, object], payload)


def response_json_object_list(response: JsonResponse) -> list[dict[str, object]]:
    """Return a JSON object list with an explicit test-facing type."""
    payload = response.json()
    if not isinstance(payload, list):
        raise AssertionError("Expected response JSON payload to be a list")
    return cast(list[dict[str, object]], payload)


def response_json_string(response: JsonResponse, key: str) -> str:
    """Read one required string field from a JSON object response."""
    value = response_json_object(response)[key]
    if not isinstance(value, str):
        raise AssertionError(f"Expected response field {key!r} to be a string")
    return value
