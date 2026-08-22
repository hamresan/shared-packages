"""FastAPI adapter composition for presentation tests."""

from integration_auth.application.contracts.authentication import IntegrationRequestAuthenticator
from integration_auth.application.contracts.authorization import IntegrationRequestAuthorizer
from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from integration_auth.presentation.factory import (
    FastApiIntegrationAuth,
    FastApiIntegrationAuthFactory,
)
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder


def build_fastapi_integration_auth(
    *,
    authenticator: IntegrationRequestAuthenticator,
    authorizer: IntegrationRequestAuthorizer,
) -> FastApiIntegrationAuth:
    """Compose the real FastAPI adapter with test application boundaries."""
    return FastApiIntegrationAuthFactory().create(
        authenticator=authenticator,
        authorizer=authorizer,
        body_hasher=Sha256BodyHasher(),
        query_encoder=CanonicalQueryEncoder(),
    )
