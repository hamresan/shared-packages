import pytest
from fastapi.security import HTTPAuthorizationCredentials
from identity_store_consumer_test_support.authentication import (
    FailingAccessTokenAuthenticator,
)

from identity_store_consumer_app.authentication import IdentityStoreActorDependency


@pytest.mark.asyncio
async def test_unexpected_authentication_failure_is_not_mapped_to_unauthorized() -> None:
    dependency = IdentityStoreActorDependency(FailingAccessTokenAuthenticator())
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token")

    with pytest.raises(RuntimeError, match="Authentication backend unavailable"):
        await dependency(credentials)
