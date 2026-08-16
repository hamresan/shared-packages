from identity.infrastructure.persistence.sqlalchemy.base import IdentityBase


def test_all_identity_tables_use_identity_prefix() -> None:
    table_names = set(IdentityBase.metadata.tables)

    assert table_names == {
        "identity_users",
        "identity_user_identities",
        "identity_otp_challenges",
        "identity_sessions",
    }
    assert all(name.startswith("identity_") for name in table_names)
