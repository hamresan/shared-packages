"""Security and identifier fakes for host-linking tests."""

from instagram_auth.application.contracts import (
    InstagramAccessTokenProtector,
    InstagramConnectionIdGenerator,
)
from instagram_auth.domain import InstagramConnectionId


class FixedInstagramConnectionIdGenerator(InstagramConnectionIdGenerator):
    def __init__(self, connection_id: InstagramConnectionId) -> None:
        self._connection_id = connection_id

    def generate(self) -> InstagramConnectionId:
        return self._connection_id


class FakeInstagramAccessTokenProtector(InstagramAccessTokenProtector):
    def protect(self, access_token: str) -> str:
        return f"protected:{access_token}"

    def unprotect(self, protected_access_token: str) -> str:
        prefix = "protected:"
        if not protected_access_token.startswith(prefix):
            raise ValueError("Credential is not protected")
        return protected_access_token[len(prefix) :]
