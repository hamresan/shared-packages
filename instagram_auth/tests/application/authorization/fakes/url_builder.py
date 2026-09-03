"""Authorization URL builder fake."""

from collections.abc import Collection

from instagram_auth.application.contracts import InstagramAuthorizationUrlBuilder
from instagram_auth.baseline import InstagramPermission


class FakeInstagramAuthorizationUrlBuilder(InstagramAuthorizationUrlBuilder):
    """Capture URL-builder inputs and return a deterministic test URL."""

    def __init__(self) -> None:
        self.redirect_uri: str | None = None
        self.state: str | None = None
        self.permissions: frozenset[InstagramPermission] = frozenset()

    def build(
        self,
        *,
        redirect_uri: str,
        state: str,
        permissions: Collection[InstagramPermission],
    ) -> str:
        self.redirect_uri = redirect_uri
        self.state = state
        self.permissions = frozenset(permissions)
        return f"https://provider.example/authorize?state={state}"
