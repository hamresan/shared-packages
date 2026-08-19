from identity.application.errors import InactiveUserError
from identity.domain import User, UserStatus


class UserStatusPolicy:
    def ensure_active(self, user: User) -> None:
        if user.status is not UserStatus.ACTIVE:
            raise InactiveUserError("User account is not active")
