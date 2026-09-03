"""Factory for secure short-lived authorization state records."""

from datetime import timedelta

from instagram_auth.application.authorization.models import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
    InstagramAuthorizationState,
)
from instagram_auth.application.contracts import Clock, StateGenerator


class InstagramAuthorizationStateFactory:
    """Create valid OAuth state records from injected security and time boundaries."""

    def __init__(
        self,
        *,
        state_generator: StateGenerator,
        clock: Clock,
        lifetime: timedelta,
    ) -> None:
        if lifetime <= timedelta(0):
            raise ValueError("Authorization state lifetime must be positive")
        self._state_generator = state_generator
        self._clock = clock
        self._lifetime = lifetime

    def create(
        self,
        *,
        redirect_uri: str,
        correlation: InstagramAuthorizationCorrelation,
    ) -> InstagramAuthorizationState:
        """Create a state record and enforce correlation invariants."""
        if not redirect_uri:
            raise ValueError("redirect_uri is required")
        if (
            correlation.flow is InstagramAuthorizationFlow.CONNECT_ACCOUNT
            and not correlation.owner_user_id
        ):
            raise ValueError("owner_user_id is required when connecting an account")
        if correlation.flow is InstagramAuthorizationFlow.LOGIN and correlation.owner_user_id:
            raise ValueError("owner_user_id must not be set for first-time login")

        now = self._clock.now()
        return InstagramAuthorizationState(
            state=self._state_generator.generate(),
            redirect_uri=redirect_uri,
            correlation=correlation,
            expires_at=now + self._lifetime,
        )
