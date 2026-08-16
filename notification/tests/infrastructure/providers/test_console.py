from io import StringIO

from notification.infrastructure.providers.console import ConsoleNotificationProvider
from tests.support import build_delivery_request


async def test_console_provider_writes_notification() -> None:
    writer = StringIO()
    provider = ConsoleNotificationProvider(writer)

    result = await provider.send(build_delivery_request())

    assert result.provider == "console"
    assert writer.getvalue() == "[sms] +96890000000: Your OTP is 123456\n"
