"""Access policy for selected Instagram account reads."""

from instagram_api.domain import InstagramAccount, InstagramConnection

from .errors import (
    InstagramAccountMismatchError,
    InstagramConnectionUnavailableError,
    InstagramPermissionRequiredError,
)

INSTAGRAM_BUSINESS_BASIC_PERMISSION = "instagram_business_basic"


class InstagramAccountAccessPolicy:
    """Validates connection eligibility and provider-account correlation."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Validate that the selected connection can read account profile data."""

        if not connection.is_usable:
            raise InstagramConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        if INSTAGRAM_BUSINESS_BASIC_PERMISSION not in connection.permissions:
            raise InstagramPermissionRequiredError(
                f"Required permission is missing: {INSTAGRAM_BUSINESS_BASIC_PERMISSION}"
            )

    def validate_account(
        self,
        connection: InstagramConnection,
        account: InstagramAccount,
    ) -> None:
        """Validate that provider data belongs to the selected connection."""

        if account.id != connection.provider_account_id:
            raise InstagramAccountMismatchError(
                "Provider account does not match the selected Instagram connection."
            )
