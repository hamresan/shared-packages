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


def test_distinguishes_literal_plus_from_space() -> None:
    encoder = CanonicalQueryEncoder()

    result = encoder.encode([("value", "+"), ("value", " ")])

    assert result == "value=%20&value=%2B"


def test_distinguishes_literal_percent_sequences_from_decoded_values() -> None:
    encoder = CanonicalQueryEncoder()

    result = encoder.encode([("value", "%2F"), ("value", "/")])

    assert result == "value=%252F&value=%2F"


def test_utf8_encodes_non_ascii_query_values_deterministically() -> None:
    result = CanonicalQueryEncoder().encode([("city", "مسقط")])

    assert result == "city=%D9%85%D8%B3%D9%82%D8%B7"


def test_empty_query_encodes_to_empty_string() -> None:
    assert CanonicalQueryEncoder().encode([]) == ""
