"""Factory for credential rotation service tests."""

from integration_auth.application.mappers.time.unix_timestamp_mapper import UnixTimestampMapper
from integration_auth.application.services.provisioning.rotate_credential import RotateCredentialService
from integration_auth.domain.policies.credential_rotation_policy import CredentialRotationPolicy
from tests.support.application.authentication.fixed_clock import FixedClock
from tests.support.application.provisioning.fixed_id_generators import (
    FixedIntegrationCredentialIdGenerator,
)
from tests.support.application.provisioning.fixed_secret_generator import (
    FixedCredentialSecretGenerator,
)
from tests.support.application.provisioning.integration_client_repository_fake import (
    IntegrationClientProvisioningRepositoryFake,
)
from tests.support.application.provisioning.integration_credential_repository_fake import (
    IntegrationCredentialProvisioningRepositoryFake,
)
from tests.support.application.provisioning.recording_secret_protector import (
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
