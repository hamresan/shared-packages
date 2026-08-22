"""Factory for credential issuance service tests."""

from integration_auth.application.mappers.time import UnixTimestampMapper
from integration_auth.application.services.provisioning.issue_credential import (
    IssueCredentialService,
)
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


def build_issue_credential_service(
    *,
    client_repository: IntegrationClientProvisioningRepositoryFake,
    credential_repository: IntegrationCredentialProvisioningRepositoryFake,
    protector: RecordingCredentialSecretProtector,
    timestamp: int,
    raw_secret: bytes,
) -> IssueCredentialService:
    """Build IssueCredentialService with deterministic provisioning dependencies."""
    return IssueCredentialService(
        client_repository=client_repository,
        credential_repository=credential_repository,
        credential_id_generator=FixedIntegrationCredentialIdGenerator("credential-new"),
        secret_generator=FixedCredentialSecretGenerator(raw_secret),
        secret_protector=protector,
        clock=FixedClock(timestamp),
        timestamp_mapper=UnixTimestampMapper(),
    )
