"""Tests for integration client grant updates."""

import asyncio

import pytest

from integration_auth.application.errors.provisioning import ProvisioningClientNotFoundError
from integration_auth.application.services.provisioning.update_client_grants import (
    UpdateIntegrationClientGrantsService,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from tests.support.application.provisioning.integration_client_repository_fake import (
    IntegrationClientProvisioningRepositoryFake,
)

CLIENT_ID = IntegrationClientId("client-123")


def test_replaces_permissions_and_scopes() -> None:
    async def run() -> None:
        repository = IntegrationClientProvisioningRepositoryFake(
            (IntegrationClient(client_id=CLIENT_ID),)
        )
        service = UpdateIntegrationClientGrantsService(repository)
        permissions = frozenset({Permission("catalog.write")})
        scopes = frozenset({IntegrationScope("store", "store-123")})

        result = await service.update(
            client_id=CLIENT_ID,
            permissions=permissions,
            scopes=scopes,
        )

        assert result.permissions == permissions
        assert result.scopes == scopes
        assert repository.updated == [result]

    asyncio.run(run())


def test_unknown_client_fails_closed() -> None:
    async def run() -> None:
        repository = IntegrationClientProvisioningRepositoryFake()
        service = UpdateIntegrationClientGrantsService(repository)

        with pytest.raises(ProvisioningClientNotFoundError):
            await service.update(
                client_id=CLIENT_ID,
                permissions=frozenset(),
                scopes=frozenset(),
            )

        assert repository.updated == []

    asyncio.run(run())
