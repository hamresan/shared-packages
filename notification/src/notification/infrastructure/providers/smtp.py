import asyncio
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from notification.application.contracts.providers import NotificationProvider
from notification.application.dto import DeliveryRequest, DeliveryResult


@dataclass(frozen=True, slots=True)
class SmtpSettings:
    host: str
    port: int
    sender: str
    username: str | None = None
    password: str | None = None
    use_tls: bool = True


class SmtpEmailProvider(NotificationProvider):
    def __init__(self, settings: SmtpSettings) -> None:
        self._settings = settings

    async def send(self, request: DeliveryRequest) -> DeliveryResult:
        await asyncio.to_thread(self._send_sync, request)
        return DeliveryResult(provider="smtp")

    def _send_sync(self, request: DeliveryRequest) -> None:
        message = EmailMessage()
        message["From"] = self._settings.sender
        message["To"] = request.recipient
        message["Subject"] = request.message.subject or ""
        message.set_content(request.message.body)
        with smtplib.SMTP(self._settings.host, self._settings.port) as client:
            if self._settings.use_tls:
                client.starttls()
            if self._settings.username is not None:
                client.login(self._settings.username, self._settings.password or "")
            client.send_message(message)
