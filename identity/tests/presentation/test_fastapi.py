from fastapi import FastAPI
from fastapi.testclient import TestClient

from identity.presentation.fastapi import FastApiIdentityAdapter
from tests.support import FakeAccessTokenAuthenticator


def build_client() -> TestClient:
    app = FastAPI()
    FastApiIdentityAdapter(FakeAccessTokenAuthenticator()).install(app)
    return TestClient(app)


def test_me_requires_bearer_token() -> None:
    response = build_client().get("/identity/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_rejects_invalid_bearer_token() -> None:
    response = build_client().get(
        "/identity/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_me_returns_authenticated_identity() -> None:
    response = build_client().get(
        "/identity/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert set(response.json()) == {"user_id", "session_id"}
