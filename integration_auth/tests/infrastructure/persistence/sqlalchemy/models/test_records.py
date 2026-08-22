"""Tests for SQLAlchemy persistence record schema constraints."""

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
    credential_index_names = {index.name for index in IntegrationCredentialRecord.__table__.indexes}
    nonce_index_names = {index.name for index in ConsumedNonceRecord.__table__.indexes}
    nonce_constraint_names = {
        constraint.name for constraint in ConsumedNonceRecord.__table__.constraints
    }

    assert "ix_integration_auth_credentials_client_status_direction" in credential_index_names
    assert "ix_integration_auth_nonce_expiry" in nonce_index_names
    assert "uq_integration_auth_nonce_client_nonce" in nonce_constraint_names
