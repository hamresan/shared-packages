"""Tests for signed integration request authentication orchestration."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.application.dto.authentication.authenticate_integration_request import (
    AuthenticateIntegrationRequest,
)
from integration_auth.application.errors.authentication import (
    IntegrationClientNotFoundError,
    InvalidIntegrationSignatureError,
    NoUsableCredentialError,
)
from integration_auth.application.errors.replay import (
    ReplayDetectedError,
    TimestampOutsideToleranceError,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from tests.support.application.authentication.authentication_request_factory import (
    build_signed_authentication_request,
)
from tests.support.application.authentication.authentication_service_factory import (
    build_authentication_service,
)
from tests.support.application.replay.atomic_nonce_store_fake import AtomicNonceStoreFake
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder

CLIENT_ID = IntegrationClientId("client-123")
SECRET = b"stage-4-authentication-secret"


def build_client() -> IntegrationClient:
    return IntegrationClient(
        client_id=CLIENT_ID,
        permissions=frozenset({Permission("orders.read")}),
        scopes=frozenset({IntegrationScope("store", "store-123")}),
    )


def build_credential(
    credential_id: str = "credential-123",
    *,
    direction: CredentialDirection = CredentialDirection.INBOUND,
) -> IntegrationCredential:
    request = CanonicalRequestBuilder().build()
    builder = IntegrationCredentialBuilder()
    builder.credential_id = IntegrationCredentialId(credential_id)
    builder.client_id = CLIENT_ID
    builder.direction = direction
    builder.issued_at = datetime.fromtimestamp(request.timestamp, tz=UTC) - timedelta(minutes=1)
    return builder.build()


def test_authenticates_valid_request_and_builds_principal() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential()
        store = AtomicNonceStoreFake()
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={credential.credential_id: SECRET},
            current_timestamp=request.timestamp,
            nonce_store=store,
        )
        authentication_request = build_signed_authentication_request(
            client_id=CLIENT_ID,
            request=request,
            secret=SECRET,
        )

        principal = await service.authenticate(authentication_request)

        assert principal.client_id == CLIENT_ID
        assert Permission("orders.read") in principal.permissions
        assert IntegrationScope("store", "store-123") in principal.scopes
        assert len(store.calls) == 1

    asyncio.run(run())


def test_rejects_unknown_client_before_credential_resolution() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        service = build_authentication_service(
            client=None,
            credentials=(),
            secrets={},
            current_timestamp=request.timestamp,
            nonce_store=AtomicNonceStoreFake(),
        )
        authentication_request = AuthenticateIntegrationRequest(
            client_id=CLIENT_ID,
            request=request,
            signature="0" * 64,
        )

        with pytest.raises(IntegrationClientNotFoundError):
            await service.authenticate(authentication_request)

    asyncio.run(run())


def test_rejects_client_without_usable_inbound_credential() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential(direction=CredentialDirection.OUTBOUND)
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={credential.credential_id: SECRET},
            current_timestamp=request.timestamp,
            nonce_store=AtomicNonceStoreFake(),
        )

        with pytest.raises(NoUsableCredentialError):
            await service.authenticate(
                build_signed_authentication_request(
                    client_id=CLIENT_ID,
                    request=request,
                    secret=SECRET,
                )
            )

    asyncio.run(run())


def test_fails_closed_when_secret_material_is_unavailable() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential()
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={},
            current_timestamp=request.timestamp,
            nonce_store=AtomicNonceStoreFake(),
        )

        with pytest.raises(InvalidIntegrationSignatureError):
            await service.authenticate(
                build_signed_authentication_request(
                    client_id=CLIENT_ID,
                    request=request,
                    secret=SECRET,
                )
            )

    asyncio.run(run())


def test_rejects_invalid_signature_without_consuming_nonce() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential()
        store = AtomicNonceStoreFake()
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={credential.credential_id: SECRET},
            current_timestamp=request.timestamp,
            nonce_store=store,
        )

        with pytest.raises(InvalidIntegrationSignatureError):
            await service.authenticate(
                AuthenticateIntegrationRequest(
                    client_id=CLIENT_ID,
                    request=request,
                    signature="0" * 64,
                )
            )

        assert store.calls == []

    asyncio.run(run())


def test_supports_multiple_credential_candidates_for_rotation_overlap() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        first = build_credential("credential-1")
        second = build_credential("credential-2")
        service = build_authentication_service(
            client=build_client(),
            credentials=(first, second),
            secrets={
                first.credential_id: b"old-secret",
                second.credential_id: SECRET,
            },
            current_timestamp=request.timestamp,
            nonce_store=AtomicNonceStoreFake(),
        )

        principal = await service.authenticate(
            build_signed_authentication_request(
                client_id=CLIENT_ID,
                request=request,
                secret=SECRET,
            )
        )

        assert principal.client_id == CLIENT_ID

    asyncio.run(run())


def test_replay_failure_is_propagated_after_valid_signature() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential()
        store = AtomicNonceStoreFake()
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={credential.credential_id: SECRET},
            current_timestamp=request.timestamp,
            nonce_store=store,
        )
        authentication_request = build_signed_authentication_request(
            client_id=CLIENT_ID,
            request=request,
            secret=SECRET,
        )

        await service.authenticate(authentication_request)
        with pytest.raises(ReplayDetectedError):
            await service.authenticate(authentication_request)

    asyncio.run(run())


def test_stale_signed_request_is_rejected_by_replay_protection() -> None:
    async def run() -> None:
        request = CanonicalRequestBuilder().build()
        credential = build_credential()
        service = build_authentication_service(
            client=build_client(),
            credentials=(credential,),
            secrets={credential.credential_id: SECRET},
            current_timestamp=request.timestamp + 301,
            nonce_store=AtomicNonceStoreFake(),
        )

        with pytest.raises(TimestampOutsideToleranceError):
            await service.authenticate(
                build_signed_authentication_request(
                    client_id=CLIENT_ID,
                    request=request,
                    secret=SECRET,
                )
            )

    asyncio.run(run())
