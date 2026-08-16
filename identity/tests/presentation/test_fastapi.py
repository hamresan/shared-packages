from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identity.presentation.fastapi import FastApiIdentityAdapter
from tests.support.authentication import FakeAccessTokenAuthenticator
from tests.support.http_client import JsonHttpClient
from tests.support.http_services import (
    FakeOtpRequester,
    FakeOtpVerifier,
    FakeSessionRefresher,
    FakeSessionRevoker,
)


def build_client() -> tuple[JsonHttpClient, FakeOtpRequester, FakeSessionRevoker]:
    app = FastAPI()
    otp_requester = FakeOtpRequester()
    session_revoker = FakeSessionRevoker()
    FastApiIdentityAdapter(
        access_token_authenticator=FakeAccessTokenAuthenticator(),
        otp_requester=otp_requester,
        otp_verifier=FakeOtpVerifier(),
        session_refresher=FakeSessionRefresher(),
        session_revoker=session_revoker,
    ).install(app)
    return cast(JsonHttpClient, TestClient(app)), otp_requester, session_revoker


def test_me_requires_bearer_token() -> None:
    client, _, _ = build_client()
    response = client.get("/identity/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_rejects_invalid_bearer_token() -> None:
    client, _, _ = build_client()
    response = client.get(
        "/identity/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_me_returns_authenticated_identity() -> None:
    client, _, _ = build_client()
    response = client.get(
        "/identity/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert set(response.json()) == {"user_id", "session_id"}


def test_request_otp_maps_http_request_to_application_command() -> None:
    client, requester, _ = build_client()
    response = client.post(
        "/identity/otp/request",
        json={
            "identity_type": "mobile",
            "destination": "+96890000000",
            "purpose": "registration",
            "locale": "en",
        },
    )

    assert response.status_code == 202
    assert requester.command is not None
    assert requester.command.destination == "+96890000000"
    assert response.json()["challenge_id"] == str(requester.challenge_id)


def test_verify_and_refresh_return_auth_session_payloads() -> None:
    client, requester, _ = build_client()
    verify_response = client.post(
        "/identity/otp/verify",
        json={
            "challenge_id": str(requester.challenge_id),
            "code": "123456",
            "full_name": "Mehran",
        },
    )
    refresh_response = client.post(
        "/identity/sessions/refresh",
        json={"refresh_token": "r" * 48},
    )

    assert verify_response.status_code == 200
    assert verify_response.json()["access_token"] == "access-token"
    assert refresh_response.status_code == 200
    assert refresh_response.json()["refresh_token"] == "r" * 48


def test_revoke_returns_no_content() -> None:
    client, _, revoker = build_client()
    response = client.post(
        "/identity/sessions/revoke",
        json={"refresh_token": "r" * 48},
    )

    assert response.status_code == 204
    assert revoker.refresh_token == "r" * 48
