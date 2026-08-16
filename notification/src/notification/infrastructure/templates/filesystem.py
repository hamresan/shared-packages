from pathlib import Path

from notification.application.contracts.templates import MessageTemplateRepository
from notification.domain.enums import NotificationChannel


class FilesystemTemplateRepository(MessageTemplateRepository):
    def __init__(self, root: Path) -> None:
        self._root = root

    def get(self, template_key: str, locale: str, channel: NotificationChannel) -> str:
        path = self._root / locale / channel.value / f"{template_key}.j2"
        if not path.is_file():
            raise FileNotFoundError(f"Notification template not found: {path}")
        return path.read_text(encoding="utf-8")
