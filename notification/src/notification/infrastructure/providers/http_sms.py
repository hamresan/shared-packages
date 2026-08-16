from dataclasses import dataclass

import httpx

from notification.application.contracts.providers import NotificationProvider
from notification.application.dto import DeliveryRequest, DeliveryResult
from notification.infrastructure.providers.http_sms_response_mapper import HttpSmsResponseMapper


@dataclass(frozen=True, slots=True)
class HttpSmsSettings:
    url: str
    api_key: str
    sender: str | None = None
    timeout_seconds: float = 10.0


class HttpSmsProvider(NotificationProvider):
    def __init__(
        self,
        client: httpx.AsyncClient,
        settings: HttpSmsSettings,
        response_mapper: HttpSmsResponseMapper,
    ) -> None:
        self._client = client
        self._settings = settings
        self._response_mapper = response_mapper

    async def send(self, request: DeliveryRequest) -> DeliveryResult:
        response = await self._client.post(
            self._settings.url,
            json={
                "to": request.recipient,
                "message": request.message.body,
                "sender": self._settings.sender,
            },
            headers={"Authorization": f"Bearer {self._settings.api_key}"},
            timeout=self._settings.timeout_seconds,
        )
        response.raise_for_status()
        return DeliveryResult(
            provider="http_sms",
            provider_message_id=self._response_mapper.get_provider_message_id(response),
        )
