from datetime import UTC, datetime, timedelta
from uuid import UUID

from notification.public import NotificationReference, SendNotification

from identity.application.contracts.security import IssuedAccessToken


class FakeNotificationSender:
    def __init__(self, failures_remaining: int = 0) -> None:
        self.commands: list[SendNotification] = []
        self._failures_remaining = failures_remaining

    async def send(self, command: SendNotification) -> NotificationReference:
        self.commands.append(command)
        if self._failures_remaining > 0:
            self._failures_remaining -= 1
            raise RuntimeError("Notification dispatch failed")
        return NotificationReference(job_id=f"job-{len(self.commands)}")


class FakeAccessTokenIssuer:
    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken:
        now = datetime.now(UTC)
        return IssuedAccessToken(
            token=f"access-{user_id}-{session_id}",
            expires_at=now + timedelta(minutes=15),
        )
