"""Authorization application errors."""

from integration_auth.application.dto.authorization.authorization_result import (
    AuthorizationDecisionReason,
)


class IntegrationAuthorizationError(Exception):
    """Raised when an authenticated integration lacks required authorization."""

    def __init__(self, reason: AuthorizationDecisionReason) -> None:
        super().__init__(reason.value)
        self.reason = reason
