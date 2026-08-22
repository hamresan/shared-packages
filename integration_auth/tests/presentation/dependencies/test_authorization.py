"""Tests for FastAPI permission dependency factory."""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from integration_auth.application.dto.authorization import AuthorizationDecisionReason
from integration_auth.application.errors.authorization import IntegrationAuthorizationError
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.permission import Permission
from tests.support.presentation.adapter_factory import build_fastapi_integration_auth
from tests.support.presentation.authenticator_fake import IntegrationRequestAuthenticatorFake
from tests.support.presentation.authorizer_fake import IntegrationRequestAuthorizerFake
from tests.support.presentation.principal_builder import IntegrationPrincipalBuilder
from tests.support.presentation.signed_headers import SIGNED_HEADERS
from tests.support.presentation.store_resource_resolver import StorePathResourceResolver


def test_permission_dependency_requires_permission_and_resolved_resource() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    authorizer = IntegrationRequestAuthorizerFake()
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=authorizer,
    )
    dependency = adapter.permissions.create(
        Permission("orders.read"),
        resource_resolver=StorePathResourceResolver(),
    )
    app = FastAPI()

    @app.get("/stores/{store_id}")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(dependency)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    response = TestClient(app).get("/stores/store-123", headers=SIGNED_HEADERS)

    assert response.status_code == 200
    assert response.json() == {"client_id": "client-123"}
    assert authorizer.requirements == [
        (
            principal,
            Permission("orders.read"),
            IntegrationResource("store", "store-123"),
        )
    ]


def test_permission_only_dependency_passes_no_resource() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    authorizer = IntegrationRequestAuthorizerFake()
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=authorizer,
    )
    dependency = adapter.permissions.create(Permission("orders.read"))
    app = FastAPI()

    @app.get("/orders")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(dependency)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    response = TestClient(app).get("/orders", headers=SIGNED_HEADERS)

    assert response.status_code == 200
    assert authorizer.requirements == [(principal, Permission("orders.read"), None)]


def test_authorization_failure_is_mapped_to_403_without_exposing_reason() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    authorizer = IntegrationRequestAuthorizerFake(
        error=IntegrationAuthorizationError(AuthorizationDecisionReason.MISSING_RESOURCE_SCOPE)
    )
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=authorizer,
    )
    dependency = adapter.permissions.create(
        Permission("orders.read"),
        resource_resolver=StorePathResourceResolver(),
    )
    app = FastAPI()

    @app.get("/stores/{store_id}")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(dependency)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    response = TestClient(app).get("/stores/store-999", headers=SIGNED_HEADERS)

    assert response.status_code == 403
    assert response.json() == {"detail": "integration is not authorized for this operation"}
    assert "missing_resource_scope" not in response.text
