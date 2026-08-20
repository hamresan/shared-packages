from dataclasses import dataclass
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identity.presentation.fastapi import FastApiIdentityAdapter
from identity.presentation.request_metadata import RequestMetadata
from identity.presentation.schemas import MAX_REFRESH_TOKEN_LENGTH
from tests.support.authentication import FakeAccessTokenAuthenticator
from tests.support.http_client import JsonHttpClient
from tests.support.http_services import (
    FakeOtpRequester,
    FakeOtpVerifier,
    FakeSessionBulkRevoker,
    FakeSessionRefresher,
    FakeSessionRevoker,
)
from tests.support.request_metadata import FixedRequestMetadataResolver


@dataclass(frozen=True, slots=True)
class HttpTestContext:
    client: JsonHttpClient
    otp_requester: FakeOtpRequester
    otp_verifier: FakeOtpVerifier
    session_refresher: FakeSessionRefresher
    session_revoker: FakeSessionRevoker
    session_bulk_revoker: FakeSessionBulkRevoker


def build_client() -> HttpTestContext:
    app = FastAPI()
    otp_requester = FakeOtpRequester()
    otp_verifier = FakeOtpVerifier()
    session_refresher = FakeSessionRefresher()
    session_revoker = FakeSessionRevoker()
    session_bulk_revoker = FakeSessionBulkRevoker()
    resolver = FixedRequestMetadataResolver(
        RequestMetadata(ip_address="203.0.113.8", device_info="trusted-test-agent")
    )
    FastApiIdentityAdapter(
        access_token_authenticator=FakeAccessTokenAuthenticator(),
        otp_requester=otp_requester,
        otp_verifier=otp_verifier,
        session_refresher=session_refresher,
        session_revoker=session_revoker,
        session_bulk_revoker=session_bulk_revoker,
        request_metadata_resolver=resolver,
    ).install(app)
    return HttpTestContext(
        client=cast(JsonHttpClient, TestClient(app)),
        otp_requester=otp_requester,
        otp_verifier=otp_verifier,
        session_refresher=session_refresher,
        session_revoker=session_revoker,
        session_bulk_revoker=session_bulk_revoker,
    )


def test_me_requires_bearer_token() -> None:
    context = build_client()
    response = context.client.get("/identity/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_me_rejects_invalid_bearer_token() -> None:
    context = build_client()
    response = context.client.get(
        "/identity/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_me_returns_authenticated_identity() -> None:
    context = build_client()
    response = context.client.get(
        "/identity/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert set(response.json()) == {"user_id", "session_id"}


def test_request_otp_maps_http_request_to_application_command() -> None:
    context = build_client()
    response = context.client.post(
        "/identity/otp/request",
        json={
            "identity_type": "mobile",
            "destination": "+96890000000",
            "purpose": "registration",
            "locale": "en",
        },
    )

    assert response.status_code == 202
    assert context.otp_requester.command is not None
    assert context.otp_requester.command.destination == "+96890000000"
    assert context.otp_requester.command.ip_address == "203.0.113.8"
    assert response.json()["challenge_id"] == str(context.otp_requester.challenge_id)


def test_request_otp_rejects_unsupported_public_purpose() -> None:
    context = build_client()
    response = context.client.post(
        "/identity/otp/request",
        json={
            "identity_type": "mobile",
            "destination": "+96890000000",
            "purpose": "account_recovery",
            "locale": "en",
        },
    )

    assert response.status_code == 422
    assert context.otp_requester.command is None


def test_verify_and_refresh_use_resolved_request_metadata() -> None:
    context = build_client()
    verify_response = context.client.post(
        "/identity/otp/verify",
        json={
            "challenge_id": str(context.otp_requester.challenge_id),
            "code": "123456",
            "full_name": "Mehran",
            "ip_address": "198.51.100.99",
            "device_info": "forged-client-device",
        },
    )
    refresh_response = context.client.post(
        "/identity/sessions/refresh",
        json={
            "refresh_token": "r" * 48,
            "ip_address": "198.51.100.99",
            "device_info": "forged-client-device",
        },
    )

    assert verify_response.status_code == 200
    assert refresh_response.status_code == 200
    assert context.otp_verifier.command is not None
    assert context.otp_verifier.command.ip_address == "203.0.113.8"
    assert context.otp_verifier.command.device_info == "trusted-test-agent"
    assert context.session_refresher.command is not None
    assert context.session_refresher.command.ip_address == "203.0.113.8"
    assert context.session_refresher.command.device_info == "trusted-test-agent"


def test_refresh_rejects_oversized_token_before_service_call() -> None:
    context = build_client()

    response = context.client.post(
        "/identity/sessions/refresh",
        json={"refresh_token": "r" * (MAX_REFRESH_TOKEN_LENGTH + 1)},
    )

    assert response.status_code == 422
    assert context.session_refresher.command is None


def test_revoke_returns_no_content() -> None:
    context = build_client()
    response = context.client.post(
        "/identity/sessions/revoke",
        json={"refresh_token": "r" * 48},
    )

    assert response.status_code == 204
    assert context.session_revoker.refresh_token == "r" * 48


def test_revoke_rejects_oversized_token_before_service_call() -> None:
    context = build_client()

    response = context.client.post(
        "/identity/sessions/revoke",
        json={"refresh_token": "r" * (MAX_REFRESH_TOKEN_LENGTH + 1)},
    )

    assert response.status_code == 422
    assert context.session_revoker.refresh_token is None


def test_revoke_all_requires_authentication() -> None:
    context = build_client()

    response = context.client.post("/identity/sessions/revoke-all")

    assert response.status_code == 401
    assert context.session_bulk_revoker.user_id is None


def test_revoke_all_uses_authenticated_user() -> None:
    context = build_client()

    response = context.client.post(
        "/identity/sessions/revoke-all",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 204
    assert context.session_bulk_revoker.user_id is not None
