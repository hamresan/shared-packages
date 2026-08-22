"""Tests for secure provisioning generators."""

from integration_auth.infrastructure.security.generators import (
    SecretsCredentialSecretGenerator,
    UuidIntegrationClientIdGenerator,
    UuidIntegrationCredentialIdGenerator,
)


def test_secret_generator_returns_256_bit_non_repeating_secrets() -> None:
    generator = SecretsCredentialSecretGenerator()

    first = generator.generate()
    second = generator.generate()

    assert len(first) == 32
    assert len(second) == 32
    assert first != second


def test_uuid_generators_return_distinct_valid_identifiers() -> None:
    client_generator = UuidIntegrationClientIdGenerator()
    credential_generator = UuidIntegrationCredentialIdGenerator()

    first_client = client_generator.generate()
    second_client = client_generator.generate()
    first_credential = credential_generator.generate()
    second_credential = credential_generator.generate()

    assert first_client != second_client
    assert first_credential != second_credential
    assert len(first_client.value) == 36
    assert len(first_credential.value) == 36
