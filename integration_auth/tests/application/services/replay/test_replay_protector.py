"""Tests for ReplayProtector."""

import asyncio

import pytest

from integration_auth.application.errors.replay import (
    ReplayDetectedError,
    TimestampOutsideToleranceError,
)
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from tests.support.application.replay.atomic_nonce_store_fake import AtomicNonceStoreFake
from tests.support.application.replay.replay_protector_factory import build_replay_protector
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder


def test_accepts_first_valid_client_nonce() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()
        client_id = IntegrationClientId("client-123")

        await protector.protect(
            client_id=client_id,
            request=request,
            current_timestamp=request.timestamp,
        )

        assert store.calls == [(client_id, request.nonce, request.timestamp + 600)]

    asyncio.run(run())


def test_rejects_duplicate_nonce_for_same_client() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()
        client_id = IntegrationClientId("client-123")

        await protector.protect(
            client_id=client_id,
            request=request,
            current_timestamp=request.timestamp,
        )

        with pytest.raises(ReplayDetectedError, match="already been consumed"):
            await protector.protect(
                client_id=client_id,
                request=request,
                current_timestamp=request.timestamp + 1,
            )

    asyncio.run(run())


def test_rejects_stale_timestamp_without_consuming_nonce() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()

        with pytest.raises(TimestampOutsideToleranceError, match="clock skew"):
            await protector.protect(
                client_id=IntegrationClientId("client-123"),
                request=request,
                current_timestamp=request.timestamp + 301,
            )

        assert store.calls == []

    asyncio.run(run())


def test_rejects_future_timestamp_without_consuming_nonce() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()

        with pytest.raises(TimestampOutsideToleranceError):
            await protector.protect(
                client_id=IntegrationClientId("client-123"),
                request=request,
                current_timestamp=request.timestamp - 301,
            )

        assert store.calls == []

    asyncio.run(run())


def test_same_nonce_is_scoped_per_integration_client() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()

        await protector.protect(
            client_id=IntegrationClientId("client-a"),
            request=request,
            current_timestamp=request.timestamp,
        )
        await protector.protect(
            client_id=IntegrationClientId("client-b"),
            request=request,
            current_timestamp=request.timestamp,
        )

    asyncio.run(run())


def test_concurrent_duplicate_requests_do_not_both_succeed() -> None:
    async def run() -> None:
        store = AtomicNonceStoreFake()
        protector = build_replay_protector(store)
        request = CanonicalRequestBuilder().build()
        client_id = IntegrationClientId("client-123")

        results = await asyncio.gather(
            protector.protect(
                client_id=client_id,
                request=request,
                current_timestamp=request.timestamp,
            ),
            protector.protect(
                client_id=client_id,
                request=request,
                current_timestamp=request.timestamp,
            ),
            return_exceptions=True,
        )

        assert sum(result is None for result in results) == 1
        assert sum(isinstance(result, ReplayDetectedError) for result in results) == 1

    asyncio.run(run())
