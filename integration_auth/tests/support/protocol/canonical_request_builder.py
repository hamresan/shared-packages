"""Test builder for canonical request protocol values."""

from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class CanonicalRequestBuilder:
    """Build valid canonical requests with focused test overrides."""

    def __init__(self) -> None:
        self.method = "POST"
        self.path = "/api/catalog/products"
        self.canonical_query = "page=2&tag=blue%20sky&tag=sale"
        self.timestamp = 1787390042
        self.nonce = "7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3"
        self.body_sha256 = "541dffad76efde94986c635a29f19b29df65fc7d07b44da2576ce9fec007a802"

    def build(self) -> CanonicalRequest:
        return CanonicalRequest(
            method=self.method,
            path=self.path,
            canonical_query=self.canonical_query,
            timestamp=self.timestamp,
            nonce=self.nonce,
            body_sha256=self.body_sha256,
        )
