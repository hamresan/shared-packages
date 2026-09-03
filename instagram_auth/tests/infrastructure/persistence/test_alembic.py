from instagram_auth.infrastructure.persistence import (
    get_instagram_auth_metadata,
    is_instagram_auth_table,
)


def test_package_metadata_exposes_only_prefixed_connection_table() -> None:
    metadata = get_instagram_auth_metadata()

    assert "instagram_auth_connections" in metadata.tables
    assert is_instagram_auth_table("instagram_auth_connections") is True
    assert is_instagram_auth_table("users") is False
