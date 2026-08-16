from email.message import EmailMessage
from types import TracebackType


class RecordingSmtpClient:
    last_instance: "RecordingSmtpClient | None" = None

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.tls_started = False
        self.login_credentials: tuple[str, str] | None = None
        self.message: EmailMessage | None = None
        RecordingSmtpClient.last_instance = self

    def __enter__(self) -> "RecordingSmtpClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def starttls(self) -> None:
        self.tls_started = True

    def login(self, username: str, password: str) -> None:
        self.login_credentials = (username, password)

    def send_message(self, message: EmailMessage) -> None:
        self.message = message
