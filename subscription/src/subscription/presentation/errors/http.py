from dataclasses import dataclass

from fastapi import HTTPException, status

from subscription.application import (
    PlanCodeAlreadyExistsError,
    PlanNotFoundError,
    PlanUnavailableError,
    SubscriptionNotFoundError,
)


class SubscriptionAuthorizationDeniedError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SubscriptionHttpErrorMapper:
    def map(self, error: Exception) -> HTTPException:
        if isinstance(error, SubscriptionAuthorizationDeniedError):
            return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        if isinstance(error, (PlanNotFoundError, SubscriptionNotFoundError)):
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
        if isinstance(error, PlanCodeAlreadyExistsError):
            return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        if isinstance(error, PlanUnavailableError):
            return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
        if isinstance(error, ValueError):
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            )
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
