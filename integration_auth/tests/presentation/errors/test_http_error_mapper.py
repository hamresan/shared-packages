"""Tests for FastAPI integration security error mapping."""

from integration_auth.presentation.errors.http_error_mapper import FastApiIntegrationErrorMapper


def test_authentication_error_is_401_with_generic_detail() -> None:
    error = FastApiIntegrationErrorMapper().authentication_error()

    assert error.status_code == 401
    assert error.detail == "invalid integration authentication"


def test_authorization_error_is_403_with_generic_detail() -> None:
    error = FastApiIntegrationErrorMapper().authorization_error()

    assert error.status_code == 403
    assert error.detail == "integration is not authorized for this operation"
