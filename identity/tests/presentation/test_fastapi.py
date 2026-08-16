from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identity.presentation.fastapi import FastApiIdentityAdapter
from identity.public import AuthenticatedPrincipal


class FakeAccessTokenAuthenticator:
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        assert access_token == "valid-token"
        now = datetime.now(UTC)
        return AuthenticatedPrincipal(
            user_id=uuid4(),
            session_id=uuid4(),
            authentication_method="otp",
            issued_at=now,
            expires_at=now + timedelta(minutes=15),
        )


def test_me_requires_bearer_token() -> None:
    app = FastAPI()
    FastApiIdentityAdapter(FakeAccessTokenAuthenticator()).install(app)

    response = TestClient(app).get("/identity/me")

    assert response.status_code == 401


def test_me_returns_authenticated_identity() -> None:
    app = FastAPI()
    FastApiIdentityAdapter(FakeAccessTokenAuthenticator()).install(app)

    response = TestClient(app).get(
        "/identity/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert set(response.json()) == {"user_id", "session_id"}
