"""Translate stable application exceptions to documented HTTP statuses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from scheduling.application.errors import (
    CalendarAlreadyExistsError,
    CalendarNotFoundError,
    CalendarVersionConflictError,
)


def install_calendar_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(CalendarNotFoundError)
    async def not_found(_request: Request, error: CalendarNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(CalendarAlreadyExistsError)
    async def already_exists(_request: Request, error: CalendarAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(CalendarVersionConflictError)
    async def conflict(_request: Request, error: CalendarVersionConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(PermissionError)
    async def forbidden(_request: Request, _error: PermissionError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": "Access denied."})

    @app.exception_handler(ValueError)
    async def invalid(_request: Request, error: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})
