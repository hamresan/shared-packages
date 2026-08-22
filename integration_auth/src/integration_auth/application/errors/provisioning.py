"""Provisioning application errors."""


class IntegrationProvisioningError(Exception):
    """Base error for integration provisioning failures."""


class ProvisioningClientNotFoundError(IntegrationProvisioningError):
    """Raised when a provisioning operation targets an unknown client."""


class ProvisioningCredentialNotFoundError(IntegrationProvisioningError):
    """Raised when a lifecycle operation targets an unknown credential."""
