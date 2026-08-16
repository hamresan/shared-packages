import httpx

from notification.infrastructure.providers.http_sms_response_mapper import HttpSmsResponseMapper


def test_response_mapper_returns_message_id() -> None:
    response = httpx.Response(200, json={"message_id": "provider-123"})

    assert HttpSmsResponseMapper().get_provider_message_id(response) == "provider-123"


def test_response_mapper_returns_none_for_empty_response() -> None:
    response = httpx.Response(204)

    assert HttpSmsResponseMapper().get_provider_message_id(response) is None


def test_response_mapper_returns_none_for_non_object_payload() -> None:
    response = httpx.Response(200, json=["provider-123"])

    assert HttpSmsResponseMapper().get_provider_message_id(response) is None


def test_response_mapper_returns_none_for_non_string_message_id() -> None:
    response = httpx.Response(200, json={"message_id": 123})

    assert HttpSmsResponseMapper().get_provider_message_id(response) is None
