"""Factory for authentication-service tests."""

from integration_auth.application.mappers.authentication import (
    IntegrationPrincipalMapper,
)
from integration_auth.application.services.authentication import (
    AuthenticateIntegrationRequestService,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.policies import (
    CredentialAuthenticationPolicy,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import (
    HmacSha256RequestSigner,
)
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_verifier import (
    HmacSha256RequestVerifier,
)
from integration_auth.protocol.canonicalization.canonical_request_serializer import (
    CanonicalRequestSerializer,
)
from tests.support.application.authentication.credential_secret_provider_fake import (
    CredentialSecretProviderFake,
)
from tests.support.application.authentication.fixed_clock import FixedClock
from tests.support.application.authentication.integration_client_repository_fake import (
    IntegrationClientRepositoryFake,
)
from tests.support.application.authentication.integration_credential_repository_fake import (
    IntegrationCredentialRepositoryFake,
)
from tests.support.application.replay.atomic_nonce_store_fake import AtomicNonceStoreFake
from tests.support.application.replay.replay_protector_factory import build_replay_protector


def build_authentication_service(
    *,
    client: IntegrationClient | None,
    credentials: tuple[IntegrationCredential, ...],
    secrets: dict[IntegrationCredentialId, bytes],
    current_timestamp: int,
    nonce_store: AtomicNonceStoreFake,
) -> AuthenticateIntegrationRequestService:
    """Build Stage 4 authentication orchestration with real security components."""
    signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
    return AuthenticateIntegrationRequestService(
        client_repository=IntegrationClientRepositoryFake(client),
        credential_repository=IntegrationCredentialRepositoryFake(credentials),
        secret_provider=CredentialSecretProviderFake(secrets),
        request_verifier=HmacSha256RequestVerifier(signer),
        replay_protector=build_replay_protector(nonce_store),
        clock=FixedClock(current_timestamp),
        credential_policy=CredentialAuthenticationPolicy(),
        principal_mapper=IntegrationPrincipalMapper(),
    )
