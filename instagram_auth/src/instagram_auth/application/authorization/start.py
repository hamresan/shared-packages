"""Use case for starting an Instagram OAuth authorization attempt."""

from instagram_auth.application.authorization.factory import InstagramAuthorizationStateFactory
from instagram_auth.application.authorization.models import (
    InstagramAuthorizationStartResult,
    StartInstagramAuthorizationCommand,
)
from instagram_auth.application.contracts.authorization_state_store import (
    InstagramAuthorizationStateStore,
)
from instagram_auth.application.contracts.authorization_url_builder import (
    InstagramAuthorizationUrlBuilder,
)
from instagram_auth.baseline import build_requested_permissions


class StartInstagramAuthorization:
    """Create, persist, and render a secure Instagram authorization request."""

    def __init__(
        self,
        *,
        state_factory: InstagramAuthorizationStateFactory,
        state_store: InstagramAuthorizationStateStore,
        url_builder: InstagramAuthorizationUrlBuilder,
    ) -> None:
        self._state_factory = state_factory
        self._state_store = state_store
        self._url_builder = url_builder

    async def execute(
        self,
        command: StartInstagramAuthorizationCommand,
    ) -> InstagramAuthorizationStartResult:
        """Persist one-time state before returning the provider redirect URL."""
        authorization_state = self._state_factory.create(
            redirect_uri=command.redirect_uri,
            correlation=command.correlation,
        )
        await self._state_store.save(authorization_state)
        permissions = build_requested_permissions(command.optional_permissions)
        authorization_url = self._url_builder.build(
            redirect_uri=command.redirect_uri,
            state=authorization_state.state,
            permissions=permissions,
        )
        return InstagramAuthorizationStartResult(
            authorization_url=authorization_url,
            expires_at=authorization_state.expires_at,
        )
