from collections.abc import Awaitable
from typing import TypeVar

from fastapi import HTTPException, status

from business.domain.errors import (
    BranchNotFoundError,
    BusinessArchivedError,
    BusinessError,
    BusinessNotFoundError,
    BusinessPermissionDeniedError,
    LastActiveOwnerError,
    MembershipAlreadyExistsError,
    MembershipInvalidStateError,
    MembershipNotFoundError,
    OwnershipTransferError,
)

ResultT = TypeVar("ResultT")


class BusinessHttpErrorMapper:
    def to_http_exception(self, error: BusinessError | ValueError) -> HTTPException:
        if isinstance(error, (BusinessNotFoundError, BranchNotFoundError, MembershipNotFoundError)):
            return HTTPException(status.HTTP_404_NOT_FOUND, str(error))
        if isinstance(error, BusinessPermissionDeniedError):
            return HTTPException(status.HTTP_403_FORBIDDEN, str(error))
        if isinstance(
            error,
            (
                BusinessArchivedError,
                LastActiveOwnerError,
                MembershipAlreadyExistsError,
                MembershipInvalidStateError,
                OwnershipTransferError,
            ),
        ):
            return HTTPException(status.HTTP_409_CONFLICT, str(error))
        return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))


class BusinessHttpExecutor:
    def __init__(self, errors: BusinessHttpErrorMapper) -> None:
        self._errors = errors

    async def run(self, action: Awaitable[ResultT]) -> ResultT:
        try:
            return await action
        except (BusinessError, ValueError) as error:
            raise self._errors.to_http_exception(error) from error
