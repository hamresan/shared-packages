"""Authenticate signed machine-to-machine requests."""

from integration_auth.application.contracts.authentication import (
    Clock,
    CredentialSecretProvider,
    IntegrationClientRepository,
    IntegrationCredentialRepository,
)
from integration_auth.application.contracts.crypto.request_verifier import RequestVerifier
from integration_auth.application.dto.authentication import (
    AuthenticateIntegrationRequest,
)
from integration_auth.application.errors.authentication import (
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
)
from integration_auth.application.mappers.authentication import (
    IntegrationPrincipalMapper,
)
from integration_auth.application.services.replay.replay_protector import ReplayProtector
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.policies.credential_authentication_policy import (
    CredentialAuthenticationPolicy,
)


class AuthenticateIntegrationRequestService:
    """Orchestrate integration request authentication without infrastructure details."""

    def __init__(
        self,
        *,
        client_repository: IntegrationClientRepository,
        credential_repository: IntegrationCredentialRepository,
        secret_provider: CredentialSecretProvider,
        request_verifier: RequestVerifier,
        replay_protector: ReplayProtector,
        clock: Clock,
        credential_policy: CredentialAuthenticationPolicy,
        principal_mapper: IntegrationPrincipalMapper,
    ) -> None:
        self._client_repository = client_repository
        self._credential_repository = credential_repository
        self._secret_provider = secret_provider
        self._request_verifier = request_verifier
        self._replay_protector = replay_protector
        self._clock = clock
        self._credential_policy = credential_policy
        self._principal_mapper = principal_mapper

    async def authenticate(
        self,
        authentication_request: AuthenticateIntegrationRequest,
    ) -> IntegrationPrincipal:
        client = await self._client_repository.get_by_id(authentication_request.client_id)
        if client is None:
            raise IntegrationClientNotFoundError("integration client was not found")

        current_timestamp = self._clock.now_timestamp()
        credentials = await self._credential_repository.list_for_client(client.client_id)
        usable_credentials = tuple(
            credential
            for credential in credentials
            if self._credential_policy.allows(
                credential=credential,
                client_id=client.client_id,
                current_timestamp=current_timestamp,
            )
        )
        if not usable_credentials:
            raise NoUsableCredentialError("integration client has no usable credential")

        for credential in usable_credentials:
            secret = await self._secret_provider.get_verification_secret(credential.credential_id)
            if secret is None:
                continue
            if not self._request_verifier.verify(
                authentication_request.request,
                secret,
                authentication_request.signature,
            ):
                continue

            await self._replay_protector.protect(
                client_id=client.client_id,
                request=authentication_request.request,
                current_timestamp=current_timestamp,
            )
            return self._principal_mapper.from_client(client)

        raise InvalidIntegrationSignatureError("integration request signature is invalid")
