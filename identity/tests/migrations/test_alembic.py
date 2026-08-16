from identity.migrations import identity_metadata, include_identity_name


def test_identity_metadata_contains_only_identity_tables() -> None:
    assert set(identity_metadata().tables) == {
        "identity_users",
        "identity_user_identities",
        "identity_otp_challenges",
        "identity_sessions",
    }


def test_include_identity_name_accepts_identity_tables() -> None:
    assert include_identity_name("identity_users", "table", {}) is True
    assert include_identity_name("orders", "table", {}) is False


def test_include_identity_name_follows_parent_table_for_children() -> None:
    assert (
        include_identity_name(
            "user_id",
            "column",
            {"table_name": "identity_sessions"},
        )
        is True
    )
    assert (
        include_identity_name(
            "status",
            "column",
            {"table_name": "orders"},
        )
        is False
    )


def test_include_identity_name_keeps_non_table_scopes() -> None:
    assert include_identity_name(None, "schema", {}) is True
