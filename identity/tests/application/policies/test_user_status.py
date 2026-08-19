import pytest

from identity.application.errors import InactiveUserError
from identity.application.policies.user_status import UserStatusPolicy
from identity.domain import UserStatus
from tests.support.access_tokens import build_user, utc_now


def test_user_status_policy_allows_active_user() -> None:
    now = utc_now()
    user = build_user(user_id=__import__("uuid").uuid4(), now=now)

    UserStatusPolicy().ensure_active(user)


@pytest.mark.parametrize("status", [UserStatus.PENDING, UserStatus.SUSPENDED, UserStatus.DISABLED])
def test_user_status_policy_rejects_non_active_user(status: UserStatus) -> None:
    now = utc_now()
    user = build_user(user_id=__import__("uuid").uuid4(), now=now, status=status)

    with pytest.raises(InactiveUserError):
        UserStatusPolicy().ensure_active(user)
