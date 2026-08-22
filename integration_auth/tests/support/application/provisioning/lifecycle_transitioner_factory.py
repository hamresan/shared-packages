"""Factory for credential lifecycle transition tests."""

from integration_auth.domain.policies.credential_lifecycle_policy import CredentialLifecyclePolicy
from integration_auth.domain.services.credential_lifecycle_transitioner import (
    CredentialLifecycleTransitioner,
)


def build_credential_lifecycle_transitioner() -> CredentialLifecycleTransitioner:
    """Build the real lifecycle transitioner with the real transition policy."""
    return CredentialLifecycleTransitioner(CredentialLifecyclePolicy())
