import pytest

from notification.domain.enums import NotificationChannel
from notification.infrastructure.providers import smtp as smtp_module
from notification.infrastructure.providers.smtp import SmtpEmailProvider, SmtpSettings
from tests.support import build_delivery_request
from tests.support.smtp import RecordingSmtpClient


async def test_smtp_provider_sends_email(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(smtp_module.smtplib, "SMTP", RecordingSmtpClient)
    provider = SmtpEmailProvider(
        SmtpSettings(
            host="smtp.example.test",
            port=587,
            sender="noreply@example.test",
            username="mailer",
            password="secret",
            use_tls=True,
        )
    )

    result = await provider.send(
        build_delivery_request(
            channel=NotificationChannel.EMAIL,
            recipient="user@example.test",
            subject="Your code",
        )
    )

    client = RecordingSmtpClient.last_instance
    assert client is not None
    assert result.provider == "smtp"
    assert client.host == "smtp.example.test"
    assert client.port == 587
    assert client.tls_started is True
    assert client.login_credentials == ("mailer", "secret")
    assert client.message is not None
    assert client.message["From"] == "noreply@example.test"
    assert client.message["To"] == "user@example.test"
    assert client.message["Subject"] == "Your code"
