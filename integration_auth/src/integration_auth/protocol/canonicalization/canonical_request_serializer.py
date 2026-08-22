"""Serialization of canonical requests for signing."""

from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class CanonicalRequestSerializer:
    """Serialize a canonical request to the exact signed protocol representation."""

    def serialize(self, request: CanonicalRequest) -> str:
        path_and_query = request.path
        if request.canonical_query:
            path_and_query = f"{path_and_query}?{request.canonical_query}"

        return "\n".join(
            (
                request.method,
                path_and_query,
                str(request.timestamp),
                request.nonce,
                request.body_sha256,
            )
        )
