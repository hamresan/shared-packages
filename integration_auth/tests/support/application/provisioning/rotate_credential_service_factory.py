"""Factory for credential rotation service tests."""

from integration_auth.application.mappers.time import UnixTimestampMapper
from integration_auth.application.services.provisioning.rotate_credential import (
    RotateCredentialService,
)
from integration_auth.domain.policies import CredentialRotationPolicy
from tests.support.application.authentication.fixed_clock import FixedClock
from tests.support.application.provisioning import (
    FixedCredentialSecretGenerator,
    FixedIntegrationCredentialIdGenerator,
    IntegrationClientProvisioningRepositoryFake,
    IntegrationCredentialProvisioningRepositoryFake,
    RecordingCredentialSecretProtector,
)


def build_rotate_credential_service(
    *,
    client_repository: IntegrationClientProvisioningRepositoryFake,
    credential_repository: IntegrationCredentialProvisioningRepositoryFake,
    protector: RecordingCredentialSecretProtector,
    timestamp: int,
    raw_secret: bytes,
) -> RotateCredentialService:
    """Build RotateCredentialService with deterministic provisioning dependencies."""
    return RotateCredentialService(
        client_repository=client_repository,
        credential_repository=credential_repository,
        credential_id_generator=FixedIntegrationCredentialIdGenerator("credential-rotated"),
        secret_generator=FixedCredentialSecretGenerator(raw_secret),
        secret_protector=protector,
        rotation_policy=CredentialRotationPolicy(),
        clock=FixedClock(timestamp),
        timestamp_mapper=UnixTimestampMapper(),
    )
