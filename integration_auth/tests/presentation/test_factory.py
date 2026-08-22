"""Tests for FastAPI adapter composition factory."""

from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from integration_auth.presentation import (
    FastApiIntegrationAuthFactory,
    IntegrationAuthenticationDependency,
    IntegrationPermissionDependencyFactory,
)
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder
from tests.support.presentation.authenticator_fake import IntegrationRequestAuthenticatorFake
from tests.support.presentation.authorizer_fake import IntegrationRequestAuthorizerFake
from tests.support.presentation.principal_builder import IntegrationPrincipalBuilder


def test_factory_composes_public_fastapi_dependency_surfaces() -> None:
    adapter = FastApiIntegrationAuthFactory().create(
        authenticator=IntegrationRequestAuthenticatorFake(
            principal=IntegrationPrincipalBuilder().build()
        ),
        authorizer=IntegrationRequestAuthorizerFake(),
        body_hasher=Sha256BodyHasher(),
        query_encoder=CanonicalQueryEncoder(),
    )

    assert isinstance(adapter.authenticate, IntegrationAuthenticationDependency)
    assert isinstance(adapter.permissions, IntegrationPermissionDependencyFactory)
