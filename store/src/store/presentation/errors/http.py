from fastapi import HTTPException, status


class StoreHttpErrorMapper:
    def application_error(self, error: ValueError) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )

    def store_not_found(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found",
        )
