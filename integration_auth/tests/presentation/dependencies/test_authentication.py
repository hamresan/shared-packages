"""Tests for FastAPI integration authentication dependency."""

from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from integration_auth.application.errors.authentication import InvalidIntegrationSignatureError
from integration_auth.application.errors.replay import ReplayDetectedError
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from tests.support.presentation.adapter_factory import build_fastapi_integration_auth
from tests.support.presentation.authenticator_fake import IntegrationRequestAuthenticatorFake
from tests.support.presentation.authorizer_fake import IntegrationRequestAuthorizerFake
from tests.support.presentation.principal_builder import IntegrationPrincipalBuilder
from tests.support.presentation.signed_headers import SIGNED_HEADERS


def test_authentication_dependency_maps_signed_request_and_returns_principal() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=IntegrationRequestAuthorizerFake(),
    )
    app = FastAPI()

    @app.post("/protected")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(adapter.authenticate)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    body = b'{"quantity":2}'
    response = TestClient(app).post(
        "/protected?tag=sale&tag=blue%20sky&page=2",
        content=body,
        headers=SIGNED_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {"client_id": "client-123"}
    assert len(authenticator.requests) == 1
    authentication_request = authenticator.requests[0]
    assert authentication_request.client_id.value == "client-123"
    assert authentication_request.signature == "signature-123"
    assert authentication_request.request.method == "POST"
    assert authentication_request.request.path == "/protected"
    assert authentication_request.request.canonical_query == "page=2&tag=blue%20sky&tag=sale"
    assert authentication_request.request.timestamp == 1_787_418_000
    assert authentication_request.request.nonce == "nonce-123"
    assert authentication_request.request.body_sha256 == Sha256BodyHasher().hash(body)


def test_missing_authentication_header_fails_closed_with_401() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=IntegrationRequestAuthorizerFake(),
    )
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(adapter.authenticate)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    headers = dict(SIGNED_HEADERS)
    del headers["X-Integration-Signature"]
    response = TestClient(app).get("/protected", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid integration authentication"}
    assert authenticator.requests == []


def test_invalid_timestamp_header_fails_closed_with_401() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(principal=principal)
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=IntegrationRequestAuthorizerFake(),
    )
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(adapter.authenticate)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    headers = dict(SIGNED_HEADERS)
    headers["X-Integration-Timestamp"] = "not-an-integer"
    response = TestClient(app).get("/protected", headers=headers)

    assert response.status_code == 401
    assert authenticator.requests == []


def test_invalid_signature_is_mapped_to_401_without_exposing_reason() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(
        principal=principal,
        error=InvalidIntegrationSignatureError("sensitive signature detail"),
    )
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=IntegrationRequestAuthorizerFake(),
    )
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(adapter.authenticate)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    response = TestClient(app).get("/protected", headers=SIGNED_HEADERS)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid integration authentication"}
    assert "sensitive" not in response.text


def test_replay_failure_is_mapped_to_401() -> None:
    principal = IntegrationPrincipalBuilder().build()
    authenticator = IntegrationRequestAuthenticatorFake(
        principal=principal,
        error=ReplayDetectedError("nonce was already consumed"),
    )
    adapter = build_fastapi_integration_auth(
        authenticator=authenticator,
        authorizer=IntegrationRequestAuthorizerFake(),
    )
    app = FastAPI()

    @app.get("/protected")
    async def protected(
        authenticated: Annotated[IntegrationPrincipal, Depends(adapter.authenticate)],
    ) -> dict[str, str]:
        return {"client_id": authenticated.client_id.value}

    response = TestClient(app).get("/protected", headers=SIGNED_HEADERS)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid integration authentication"}
