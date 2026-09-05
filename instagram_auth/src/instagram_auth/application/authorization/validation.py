"""Fail-closed validation policy for consumed OAuth state."""

from enum import StrEnum

from instagram_auth.application.authorization.models import (
    InstagramAuthorizationFlow,
    InstagramAuthorizationState,
    ValidatedInstagramAuthorization,
)
from instagram_auth.application.contracts.clock import Clock


class InstagramAuthorizationStateValidationFailure(StrEnum):
    """Reasons an OAuth callback state cannot be trusted."""

    MISSING = "missing"
    NOT_FOUND_OR_REUSED = "not_found_or_reused"
    EXPIRED = "expired"
    REDIRECT_URI_MISMATCH = "redirect_uri_mismatch"
    OWNER_MISMATCH = "owner_mismatch"
    CONNECTION_MISSING = "connection_missing"


class InstagramAuthorizationStateValidationError(ValueError):
    """Raised when OAuth state validation fails closed."""

    def __init__(self, failure: InstagramAuthorizationStateValidationFailure) -> None:
        self.failure = failure
        super().__init__(failure.value)


class InstagramAuthorizationStateValidator:
    """Validate consumed state against time and callback correlation."""

    def __init__(self, *, clock: Clock) -> None:
        self._clock = clock

    def validate(
        self,
        *,
        authorization_state: InstagramAuthorizationState,
        redirect_uri: str,
        authenticated_owner_user_id: str | None,
    ) -> ValidatedInstagramAuthorization:
        """Return trusted correlation context or reject the callback."""
        if self._clock.now() >= authorization_state.expires_at:
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.EXPIRED
            )
        if redirect_uri != authorization_state.redirect_uri:
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.REDIRECT_URI_MISMATCH
            )

        correlation = authorization_state.correlation
        if (
            correlation.flow is not InstagramAuthorizationFlow.LOGIN
            and authenticated_owner_user_id != correlation.owner_user_id
        ):
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.OWNER_MISMATCH
            )
        if (
            correlation.flow is InstagramAuthorizationFlow.RECONNECT_ACCOUNT
            and correlation.connection_id is None
        ):
            raise InstagramAuthorizationStateValidationError(
                InstagramAuthorizationStateValidationFailure.CONNECTION_MISSING
            )

        return ValidatedInstagramAuthorization(
            redirect_uri=authorization_state.redirect_uri,
            correlation=correlation,
        )
