from datetime import datetime

from identity.application.contracts.repositories import UserIdentityRepository, UserRepository
from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
    OtpChallengeNotFoundError,
    RegistrationNameRequiredError,
    UnsupportedOtpPurposeError,
)
from identity.application.factories.entities import UserRegistrationFactory
from identity.application.policies.user_status import UserStatusPolicy
from identity.domain import OtpChallenge, OtpPurpose, User


class VerifiedOtpUserResolver:
    def __init__(
        self,
        *,
        registration_factory: UserRegistrationFactory,
        user_status_policy: UserStatusPolicy,
    ) -> None:
        self._registration_factory = registration_factory
        self._user_status_policy = user_status_policy

    async def resolve(
        self,
        *,
        users: UserRepository,
        identities: UserIdentityRepository,
        challenge: OtpChallenge,
        full_name: str | None,
        now: datetime,
    ) -> User:
        if challenge.purpose is OtpPurpose.REGISTRATION:
            if challenge.user_id is not None:
                raise IdentityAlreadyRegisteredError("Identity is already registered")
            normalized_name = full_name.strip() if full_name else ""
            if not normalized_name:
                raise RegistrationNameRequiredError("Full name is required for registration")
            user, identity = self._registration_factory.create(
                now=now,
                full_name=normalized_name,
                identity_type=challenge.identifier_type,
                destination=challenge.normalized_destination,
            )
            await users.add(user)
            await identities.add(identity)
            return user

        if challenge.purpose is OtpPurpose.LOGIN:
            if challenge.user_id is None:
                raise IdentityNotRegisteredError("Identity is not registered")
            user = await users.get(challenge.user_id)
            if user is None:
                raise OtpChallengeNotFoundError("OTP challenge user was not found")
            self._user_status_policy.ensure_active(user)
            return user

        raise UnsupportedOtpPurposeError(f"OTP purpose is not supported: {challenge.purpose.value}")
