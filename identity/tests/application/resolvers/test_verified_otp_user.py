from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from identity.application.errors import (
    IdentityNotRegisteredError,
    RegistrationNameRequiredError,
)
from identity.application.factories.entities import OtpChallengeFactory, UserRegistrationFactory
from identity.application.policies.user_status import UserStatusPolicy
from identity.application.resolvers import VerifiedOtpUserResolver
from identity.domain import IdentityType, OtpPurpose
from tests.support.access_tokens import build_user
from tests.support.repositories import FakeUserIdentityRepository, FakeUserRepository


def build_challenge(*, purpose: OtpPurpose, user_id=None):
    now = datetime.now(UTC)
    challenge = OtpChallengeFactory(
        ttl=timedelta(minutes=5),
        resend_delay=timedelta(seconds=60),
        max_attempts=5,
    ).create(
        now=now,
        identity_type=IdentityType.EMAIL,
        destination="user@example.com",
        purpose=purpose,
        code_hash="hash",
        user_id=user_id,
        identity_id=None,
    )
    return challenge, now


@pytest.mark.asyncio
async def test_resolver_creates_registration_user_and_identity() -> None:
    challenge, now = build_challenge(purpose=OtpPurpose.REGISTRATION)
    users = FakeUserRepository()
    identities = FakeUserIdentityRepository()
    resolver = VerifiedOtpUserResolver(
        registration_factory=UserRegistrationFactory(),
        user_status_policy=UserStatusPolicy(),
    )

    user = await resolver.resolve(
        users=users,
        identities=identities,
        challenge=challenge,
        full_name="  Test User  ",
        now=now,
    )

    assert user.full_name == "Test User"
    assert users.added == [user]
    assert len(identities.identities) == 1
    assert identities.identities[0].user_id == user.id


@pytest.mark.asyncio
async def test_resolver_requires_registration_name() -> None:
    challenge, now = build_challenge(purpose=OtpPurpose.REGISTRATION)
    resolver = VerifiedOtpUserResolver(
        registration_factory=UserRegistrationFactory(),
        user_status_policy=UserStatusPolicy(),
    )

    with pytest.raises(RegistrationNameRequiredError):
        await resolver.resolve(
            users=FakeUserRepository(),
            identities=FakeUserIdentityRepository(),
            challenge=challenge,
            full_name="   ",
            now=now,
        )


@pytest.mark.asyncio
async def test_resolver_returns_existing_login_user() -> None:
    now = datetime.now(UTC)
    user = build_user(user_id=uuid4(), now=now)
    challenge, _ = build_challenge(purpose=OtpPurpose.LOGIN, user_id=user.id)
    resolver = VerifiedOtpUserResolver(
        registration_factory=UserRegistrationFactory(),
        user_status_policy=UserStatusPolicy(),
    )

    result = await resolver.resolve(
        users=FakeUserRepository([user]),
        identities=FakeUserIdentityRepository(),
        challenge=challenge,
        full_name=None,
        now=now,
    )

    assert result is user


@pytest.mark.asyncio
async def test_resolver_rejects_login_without_registered_user_id() -> None:
    challenge, now = build_challenge(purpose=OtpPurpose.LOGIN)
    resolver = VerifiedOtpUserResolver(
        registration_factory=UserRegistrationFactory(),
        user_status_policy=UserStatusPolicy(),
    )

    with pytest.raises(IdentityNotRegisteredError):
        await resolver.resolve(
            users=FakeUserRepository(),
            identities=FakeUserIdentityRepository(),
            challenge=challenge,
            full_name=None,
            now=now,
        )
