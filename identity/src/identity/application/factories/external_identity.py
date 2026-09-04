from datetime import datetime
from uuid import uuid4

from identity.domain import ExternalIdentity, User, UserStatus


class ExternalIdentityRegistrationFactory:
    def create(
        self,
        *,
        now: datetime,
        provider: str,
        subject: str,
        display_name: str,
    ) -> tuple[User, ExternalIdentity]:
        user_id = uuid4()
        user = User(
            id=user_id,
            full_name=display_name,
            status=UserStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        external_identity = ExternalIdentity(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            subject=subject,
            verified_at=now,
            created_at=now,
            updated_at=now,
        )
        return user, external_identity
