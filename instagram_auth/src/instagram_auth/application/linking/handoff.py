"""Build secret-free host identity handoff results."""

from instagram_auth.application.authorization import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
)
from instagram_auth.domain import InstagramExternalIdentity

from .models import InstagramHostIdentityHandoff, InstagramHostLinkAction


class PrepareInstagramHostIdentityHandoff:
    """Translate OAuth correlation into an explicit host identity decision point."""

    def execute(
        self,
        *,
        identity: InstagramExternalIdentity,
        correlation: InstagramAuthorizationCorrelation,
    ) -> InstagramHostIdentityHandoff:
        if correlation.flow is InstagramAuthorizationFlow.LOGIN:
            return InstagramHostIdentityHandoff(
                identity=identity,
                action=InstagramHostLinkAction.RESOLVE_LOCAL_USER,
            )
        if correlation.owner_user_id is None:
            raise ValueError("Connect-account flow requires an owner user ID")
        return InstagramHostIdentityHandoff(
            identity=identity,
            action=InstagramHostLinkAction.ATTACH_TO_EXISTING_OWNER,
            owner_user_id=correlation.owner_user_id,
        )
