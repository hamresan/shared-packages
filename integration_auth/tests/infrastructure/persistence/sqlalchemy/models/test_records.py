"""Tests for SQLAlchemy persistence record schema constraints."""

from typing import cast

from sqlalchemy import Table

from integration_auth.infrastructure.persistence.sqlalchemy.models.client_record import (
    IntegrationClientRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.models.credential_record import (
    IntegrationCredentialRecord,
)
from integration_auth.infrastructure.persistence.sqlalchemy.models.nonce_record import (
    ConsumedNonceRecord,
)


def test_all_persistence_tables_use_integration_auth_prefix() -> None:
    assert IntegrationClientRecord.__tablename__.startswith("integration_auth_")
    assert IntegrationCredentialRecord.__tablename__.startswith("integration_auth_")
    assert ConsumedNonceRecord.__tablename__.startswith("integration_auth_")


def test_credential_and_nonce_hot_paths_have_indexes_or_unique_constraints() -> None:
    credential_table = cast(Table, IntegrationCredentialRecord.__table__)
    nonce_table = cast(Table, ConsumedNonceRecord.__table__)

    credential_index_names: set[str | None] = {index.name for index in credential_table.indexes}
    nonce_index_names: set[str | None] = {index.name for index in nonce_table.indexes}
    nonce_constraint_names: set[str | None] = {
        constraint.name for constraint in nonce_table.constraints
    }

    assert "ix_integration_auth_credentials_client_status_direction" in credential_index_names
    assert "ix_integration_auth_nonce_expiry" in nonce_index_names
    assert "uq_integration_auth_nonce_client_nonce" in nonce_constraint_names
