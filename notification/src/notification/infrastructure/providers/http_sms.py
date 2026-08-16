from dataclasses import dataclass
from typing import cast

import httpx

from notification.application.contracts.providers import NotificationProvider
from notification.application.dto import DeliveryRequest, DeliveryResult


@dataclass(frozen=True, slots=True)
class HttpSmsSettings:
    url: str
    api_key: str
    sender: str | None = None
    timeout_seconds: float = 10.0


class HttpSmsProvider(NotificationProvider):
    def __init__(self, client: httpx.AsyncClient, settings: HttpSmsSettings) -> None:
        self._client = client
        self._settings = settings

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
        provider_message_id = self._extract_message_id(response)
        return DeliveryResult(provider="http_sms", provider_message_id=provider_message_id)

    @staticmethod
    def _extract_message_id(response: httpx.Response) -> str | None:
        if not response.content:
            return None

        raw_data: object = response.json()
        if not isinstance(raw_data, dict):
            return None

        data = cast(dict[str, object], raw_data)
        raw_message_id = data.get("message_id")
        return raw_message_id if isinstance(raw_message_id, str) else None
