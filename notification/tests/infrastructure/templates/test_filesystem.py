from pathlib import Path

import pytest

from notification.domain.enums import NotificationChannel
from notification.infrastructure.templates.filesystem import FilesystemTemplateRepository


def test_filesystem_repository_reads_template(tmp_path: Path) -> None:
    template_dir = tmp_path / "en" / "sms"
    template_dir.mkdir(parents=True)
    (template_dir / "auth.otp.j2").write_text("OTP {{ otp }}", encoding="utf-8")

    repository = FilesystemTemplateRepository(tmp_path)

    assert repository.get("auth.otp", "en", NotificationChannel.SMS) == "OTP {{ otp }}"


def test_filesystem_repository_raises_for_missing_template(tmp_path: Path) -> None:
    repository = FilesystemTemplateRepository(tmp_path)

    with pytest.raises(FileNotFoundError):
        repository.get("auth.otp", "en", NotificationChannel.SMS)
