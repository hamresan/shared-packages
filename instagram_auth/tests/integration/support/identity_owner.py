"""Host-owned adapter from identity principal to Instagram connection owner."""

from identity.public import AuthenticatedPrincipal


class IdentityPrincipalOwnerAdapter:
    """Map the identity package principal into the auth package external owner ID."""

    def owner_user_id(self, principal: AuthenticatedPrincipal) -> str:
        return str(principal.user_id)
