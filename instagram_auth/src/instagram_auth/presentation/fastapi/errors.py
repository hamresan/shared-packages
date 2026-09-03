"""Map application failures to transport-specific HTTP errors."""

from fastapi import HTTPException, status

from instagram_auth.application.authorization.validation import (
    InstagramAuthorizationStateValidationError,
)
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionNotFoundError,
    InstagramConnectionOwnershipError,
)


class InstagramFastApiErrorMapper:
    """Translate known application failures without leaking business logic into routes."""

    def authorization_callback(
        self,
        error: InstagramAuthorizationStateValidationError,
    ) -> HTTPException:
        del error
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Instagram authorization callback",
        )

    def connection_access(
        self,
        error: InstagramConnectionNotFoundError | InstagramConnectionOwnershipError,
    ) -> HTTPException:
        if isinstance(error, InstagramConnectionNotFoundError):
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instagram connection not found",
            )
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Instagram connection access denied",
        )
