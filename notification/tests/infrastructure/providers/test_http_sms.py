import json

import httpx

from notification.infrastructure.providers.http_sms import HttpSmsProvider, HttpSmsSettings
from notification.infrastructure.providers.http_sms_response_mapper import HttpSmsResponseMapper
from tests.support import build_delivery_request


def build_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret-key"
        payload = json.loads(request.content.decode("utf-8"))
        assert payload == {
            "to": "+96890000000",
            "message": "Your OTP is 123456",
            "sender": "Sellora",
        }
        return httpx.Response(200, json={"message_id": "sms-123"})

    return httpx.MockTransport(handler)


async def test_http_sms_provider_sends_notification() -> None:
    async with httpx.AsyncClient(transport=build_transport()) as client:
        provider = HttpSmsProvider(
            client=client,
            settings=HttpSmsSettings(
                url="https://sms.example.test/send",
                api_key="secret-key",
                sender="Sellora",
            ),
            response_mapper=HttpSmsResponseMapper(),
        )

        result = await provider.send(build_delivery_request())

    assert result.provider == "http_sms"
    assert result.provider_message_id == "sms-123"
