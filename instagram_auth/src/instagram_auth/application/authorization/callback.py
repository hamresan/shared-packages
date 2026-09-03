"""Use case for validating Instagram OAuth callback state."""

from instagram_auth.application.authorization.models import ValidatedInstagramAuthorization
from instagram_auth.application.authorization.validation import (
    InstagramAuthorizationStateValidationError,
    InstagramAuthorizationStateValidationFailure,
    InstagramAuthorizationStateValidator,
)
from instagram_auth.application.contracts.authorization_state_store import (
    InstagramAuthorizationStateStore,
)


class ValidateInstagramAuthorizationCallback:
    """Consume and validate one-time state before any code exchange occurs."""

    def __init__(
        self,
        *,
        state_store: InstagramAuthorizationStateStore,
        state_validator: InstagramAuthorizationStateValidator,
    ) -> None:
        self._state_store = state_store
        self._state_validator = state_validator

    async def execute(
        self,
        *,
        state: str | None,
        redirect_uri: str,
        authenticated_owner_user_id: str | None = None,
    ) -> ValidatedInstagramAuthorization:
        """Consume state exactly once and fail closed on any invalid callback."""
        if not state:
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.MISSING
            )

        authorization_state = await self._state_store.consume(state)
        if authorization_state is None:
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.NOT_FOUND_OR_REUSED
            )

        return self._state_validator.validate(
            authorization_state=authorization_state,
            redirect_uri=redirect_uri,
            authenticated_owner_user_id=authenticated_owner_user_id,
        )
