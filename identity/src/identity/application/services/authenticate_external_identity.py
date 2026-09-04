from identity.application.contracts.security import (
    AccessTokenIssuer,
    Clock,
    RefreshTokenGenerator,
    SecretHasher,
)
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import AuthSessionResult
from identity.application.dto_external import AuthenticateExternalIdentityCommand
from identity.application.factories.entities import SessionFactory
from identity.application.factories.external_identity import ExternalIdentityRegistrationFactory
from identity.application.policies.user_status import UserStatusPolicy


class AuthenticateExternalIdentityService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
        refresh_token_generator: RefreshTokenGenerator,
        access_token_issuer: AccessTokenIssuer,
        session_factory: SessionFactory,
        registration_factory: ExternalIdentityRegistrationFactory,
        user_status_policy: UserStatusPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._refresh_token_generator = refresh_token_generator
        self._access_token_issuer = access_token_issuer
        self._session_factory = session_factory
        self._registration_factory = registration_factory
        self._user_status_policy = user_status_policy

    async def execute(self, command: AuthenticateExternalIdentityCommand) -> AuthSessionResult:
        provider = command.provider.strip().lower()
        subject = command.subject.strip()
        display_name = command.display_name.strip()

        if not provider:
            raise ValueError("External identity provider is required")
        if not subject:
            raise ValueError("External identity subject is required")
        if not display_name:
            raise ValueError("External identity display name is required")

        now = self._clock.now()

        async with self._unit_of_work_factory() as uow:
            external_identity = await uow.external_identities.get_by_provider_subject(
                provider,
                subject,
            )

            if external_identity is None:
                user, external_identity = self._registration_factory.create(
                    now=now,
                    provider=provider,
                    subject=subject,
                    display_name=display_name,
                )
                await uow.users.add(user)
                await uow.external_identities.add(external_identity)
            else:
                user = await uow.users.get(external_identity.user_id)
                if user is None:
                    raise RuntimeError("External identity references a missing user")

            self._user_status_policy.ensure_authentication_allowed(user.status)

            refresh_token = self._refresh_token_generator.generate()
            session = self._session_factory.create(
                now=now,
                user_id=user.id,
                refresh_token_hash=self._hasher.hash(refresh_token),
                device_info=command.device_info,
                ip_address=command.ip_address,
            )
            access_token = await self._access_token_issuer.issue(user.id, session.id)
            await uow.sessions.add(session)
            await uow.commit()

        return AuthSessionResult(
            user_id=user.id,
            session_id=session.id,
            access_token=access_token.token,
            access_token_expires_at=access_token.expires_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=session.expires_at,
        )
