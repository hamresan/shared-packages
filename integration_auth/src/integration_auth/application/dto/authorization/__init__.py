"""Authorization DTO public API."""

from integration_auth.application.dto.authorization.authorization_result import (
    AuthorizationDecisionReason,
    AuthorizationResult,
)

__all__ = ("AuthorizationDecisionReason", "AuthorizationResult")
