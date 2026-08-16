from jinja2 import Environment

from notification.domain.enums import NotificationChannel
from notification.infrastructure.templates.jinja_renderer import JinjaMessageTemplateRenderer


class StubTemplateRepository:
    def __init__(self, source: str) -> None:
        self._source = source

    def get(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
    ) -> str:
        return self._source


def test_jinja_renderer_renders_sms_body() -> None:
    renderer = JinjaMessageTemplateRenderer(
        repository=StubTemplateRepository("OTP {{ otp }}"),
        environment=Environment(),
    )

    message = renderer.render(
        "auth.otp",
        "en",
        NotificationChannel.SMS,
        {"otp": "123456"},
    )

    assert message.subject is None
    assert message.body == "OTP 123456"


def test_jinja_renderer_splits_email_subject_and_body() -> None:
    renderer = JinjaMessageTemplateRenderer(
        repository=StubTemplateRepository("Your code\n---subject---\nOTP {{ otp }}"),
        environment=Environment(),
    )

    message = renderer.render(
        "auth.otp",
        "en",
        NotificationChannel.EMAIL,
        {"otp": "123456"},
    )

    assert message.subject == "Your code"
    assert message.body == "OTP 123456"
