import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from identity.presentation.fastapi import AuthenticatedUserDependency
from tests.support.authentication import (
    FailingAccessTokenAuthenticator,
    FakeAccessTokenAuthenticator,
)


@pytest.mark.asyncio
async def test_invalid_access_token_maps_to_unauthorized() -> None:
    dependency = AuthenticatedUserDependency(FakeAccessTokenAuthenticator())
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

    with pytest.raises(HTTPException) as exc_info:
        await dependency(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


@pytest.mark.asyncio
async def test_unexpected_authentication_failure_is_not_masked_as_unauthorized() -> None:
    dependency = AuthenticatedUserDependency(FailingAccessTokenAuthenticator())
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")

    with pytest.raises(RuntimeError, match="Authentication backend unavailable"):
        await dependency(credentials)
