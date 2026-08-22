"""Tests for integration client registration."""

import asyncio

from integration_auth.application.services.provisioning.register_integration_client import (
    RegisterIntegrationClientService,
)
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from tests.support.application.provisioning.fixed_id_generators import (
    FixedIntegrationClientIdGenerator,
)
from tests.support.application.provisioning.integration_client_repository_fake import (
    IntegrationClientProvisioningRepositoryFake,
)


def test_registers_client_with_explicit_grants() -> None:
    async def run() -> None:
        repository = IntegrationClientProvisioningRepositoryFake()
        service = RegisterIntegrationClientService(
            client_id_generator=FixedIntegrationClientIdGenerator("client-new"),
            repository=repository,
        )
        permissions = frozenset({Permission("orders.read")})
        scopes = frozenset({IntegrationScope("store", "store-123")})

        client = await service.register(permissions=permissions, scopes=scopes)

        assert client.client_id.value == "client-new"
        assert client.permissions == permissions
        assert client.scopes == scopes
        assert repository.added == [client]

    asyncio.run(run())


def test_registers_client_with_empty_grants_by_default() -> None:
    async def run() -> None:
        repository = IntegrationClientProvisioningRepositoryFake()
        service = RegisterIntegrationClientService(
            client_id_generator=FixedIntegrationClientIdGenerator(),
            repository=repository,
        )

        client = await service.register()

        assert client.permissions == frozenset()
        assert client.scopes == frozenset()

    asyncio.run(run())
