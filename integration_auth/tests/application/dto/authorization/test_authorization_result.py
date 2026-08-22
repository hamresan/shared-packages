"""Tests for AuthorizationResult."""

import pytest

from integration_auth.application.dto.authorization.authorization_result import (
    AuthorizationDecisionReason,
    AuthorizationResult,
)


def test_allowed_result_is_allowed() -> None:
    result = AuthorizationResult.allow()

    assert result.allowed
    assert result.reason is AuthorizationDecisionReason.ALLOWED


def test_denied_result_is_not_allowed() -> None:
    result = AuthorizationResult.deny(AuthorizationDecisionReason.MISSING_PERMISSION)

    assert not result.allowed
    assert result.reason is AuthorizationDecisionReason.MISSING_PERMISSION


def test_denied_result_rejects_allowed_reason() -> None:
    with pytest.raises(ValueError, match="denial reason"):
        AuthorizationResult.deny(AuthorizationDecisionReason.ALLOWED)
