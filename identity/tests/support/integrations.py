from datetime import UTC, datetime, timedelta
from uuid import UUID

from notification.public import NotificationReference, SendNotification

from identity.application.contracts.security import IssuedAccessToken


class FakeNotificationSender:
    def __init__(self) -> None:
        self.commands: list[SendNotification] = []

    async def send(self, command: SendNotification) -> NotificationReference:
        self.commands.append(command)
        return NotificationReference(job_id=f"job-{len(self.commands)}")


class FakeAccessTokenIssuer:
    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken:
        now = datetime.now(UTC)
        return IssuedAccessToken(
            token=f"access-{user_id}-{session_id}",
            expires_at=now + timedelta(minutes=15),
        )
