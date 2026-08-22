"""Map integration authentication and authorization failures to HTTP errors."""

from fastapi import HTTPException, status


class FastApiIntegrationErrorMapper:
    """Create fail-closed HTTP errors without exposing security-sensitive details."""

    def authentication_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid integration authentication",
        )

    def authorization_error(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="integration is not authorized for this operation",
        )
