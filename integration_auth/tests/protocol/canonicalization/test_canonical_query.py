from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder


def test_encodes_sorts_and_preserves_duplicate_query_parameters() -> None:
    encoder = CanonicalQueryEncoder()

    result = encoder.encode(
        [
            ("tag", "sale"),
            ("page", "2"),
            ("tag", "blue sky"),
            ("symbol", "/?&="),
        ]
    )

    assert result == "page=2&symbol=%2F%3F%26%3D&tag=blue%20sky&tag=sale"


def test_empty_query_encodes_to_empty_string() -> None:
    assert CanonicalQueryEncoder().encode([]) == ""
