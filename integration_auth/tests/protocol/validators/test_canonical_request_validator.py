import pytest

from integration_auth.protocol.validators.canonical_request_validator import CanonicalRequestValidator

VALID_METHOD = "POST"
VALID_PATH = "/api/items"
VALID_QUERY = "a=1&b=2"
VALID_TIMESTAMP = 1787390042
VALID_NONCE = "nonce-123"
VALID_BODY_SHA256 = "a" * 64


def test_accepts_valid_canonical_request_values() -> None:
    CanonicalRequestValidator().validate(
        method=VALID_METHOD,
        path=VALID_PATH,
        canonical_query=VALID_QUERY,
        timestamp=VALID_TIMESTAMP,
        nonce=VALID_NONCE,
        body_sha256=VALID_BODY_SHA256,
    )


def test_rejects_noncanonical_method() -> None:
    with pytest.raises(ValueError, match="method"):
        CanonicalRequestValidator().validate(
            method="post",
            path=VALID_PATH,
            canonical_query=VALID_QUERY,
            timestamp=VALID_TIMESTAMP,
            nonce=VALID_NONCE,
            body_sha256=VALID_BODY_SHA256,
        )


@pytest.mark.parametrize("path", ["api/items", "/api?x=1", "/api#fragment", "/api\nitems"])
def test_rejects_invalid_path(path: str) -> None:
    with pytest.raises(ValueError, match="path"):
        CanonicalRequestValidator().validate(
            method=VALID_METHOD,
            path=path,
            canonical_query=VALID_QUERY,
            timestamp=VALID_TIMESTAMP,
            nonce=VALID_NONCE,
            body_sha256=VALID_BODY_SHA256,
        )


@pytest.mark.parametrize("query", ["?a=1", "a=1#fragment", "a=1\nb=2"])
def test_rejects_invalid_canonical_query(query: str) -> None:
    with pytest.raises(ValueError, match="canonical_query"):
        CanonicalRequestValidator().validate(
            method=VALID_METHOD,
            path=VALID_PATH,
            canonical_query=query,
            timestamp=VALID_TIMESTAMP,
            nonce=VALID_NONCE,
            body_sha256=VALID_BODY_SHA256,
        )


def test_rejects_negative_timestamp() -> None:
    with pytest.raises(ValueError, match="timestamp"):
        CanonicalRequestValidator().validate(
            method=VALID_METHOD,
            path=VALID_PATH,
            canonical_query=VALID_QUERY,
            timestamp=-1,
            nonce=VALID_NONCE,
            body_sha256=VALID_BODY_SHA256,
        )


def test_rejects_invalid_nonce() -> None:
    with pytest.raises(ValueError, match="nonce"):
        CanonicalRequestValidator().validate(
            method=VALID_METHOD,
            path=VALID_PATH,
            canonical_query=VALID_QUERY,
            timestamp=VALID_TIMESTAMP,
            nonce="bad nonce",
            body_sha256=VALID_BODY_SHA256,
        )


def test_rejects_invalid_body_hash() -> None:
    with pytest.raises(ValueError, match="body_sha256"):
        CanonicalRequestValidator().validate(
            method=VALID_METHOD,
            path=VALID_PATH,
            canonical_query=VALID_QUERY,
            timestamp=VALID_TIMESTAMP,
            nonce=VALID_NONCE,
            body_sha256="ABC",
        )
