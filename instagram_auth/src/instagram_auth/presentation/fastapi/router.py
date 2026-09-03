"""Thin FastAPI routes over transport-independent Instagram auth use cases."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, Response, status

from instagram_auth.application.authorization.models import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
    StartInstagramAuthorizationCommand,
)
from instagram_auth.application.authorization.validation import (
    InstagramAuthorizationStateValidationError,
)
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionNotFoundError,
    InstagramConnectionOwnershipError,
)
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

from .config import InstagramFastApiConfig
from .dependencies import InstagramFastApiDependencies
from .schemas import InstagramAuthorizationStartResponse, InstagramConnectionResponse


def create_instagram_auth_router(
    *,
    config: InstagramFastApiConfig,
    dependencies: InstagramFastApiDependencies,
) -> APIRouter:
    """Create package routes without owning host prefixing or session behavior."""
    router = APIRouter()

    @router.get("/instagram/auth/start", response_model=InstagramAuthorizationStartResponse)
    async def start_authorization(
        request: Request,
        flow: InstagramAuthorizationFlow = InstagramAuthorizationFlow.LOGIN,
        optional_permissions: list[InstagramPermission] = Query(default=[]),
    ) -> InstagramAuthorizationStartResponse:
        owner_user_id = None
        if flow is InstagramAuthorizationFlow.CONNECT_ACCOUNT:
            owner_user_id = await dependencies.owner_context.require_owner_user_id(request)

        result = await dependencies.start_authorization.execute(
            StartInstagramAuthorizationCommand(
                redirect_uri=config.redirect_uri,
                correlation=InstagramAuthorizationCorrelation(
                    flow=flow,
                    owner_user_id=owner_user_id,
                ),
                optional_permissions=optional_permissions,
            )
        )
        return InstagramAuthorizationStartResponse(
            authorization_url=result.authorization_url,
            expires_at=result.expires_at,
        )

    @router.get("/instagram/auth/callback")
    async def authorization_callback(
        request: Request,
        code: str,
        state_value: str | None = Query(default=None, alias="state"),
    ) -> Response:
        owner_user_id = await dependencies.owner_context.optional_owner_user_id(request)
        try:
            authorization = await dependencies.validate_callback.execute(
                state=state_value,
                redirect_uri=config.redirect_uri,
                authenticated_owner_user_id=owner_user_id,
            )
        except InstagramAuthorizationStateValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Instagram authorization callback",
            ) from exc
        return await dependencies.callback_responder.respond(
            authorization_code=code,
            authorization=authorization,
        )

    @router.get("/instagram/connections", response_model=list[InstagramConnectionResponse])
    async def list_connections(request: Request) -> list[InstagramConnectionResponse]:
        owner_user_id = await dependencies.owner_context.require_owner_user_id(request)
        connections = await dependencies.list_connections.execute(owner_user_id=owner_user_id)
        return [dependencies.connection_mapper.map(connection) for connection in connections]

    @router.get(
        "/instagram/connections/{connection_id}",
        response_model=InstagramConnectionResponse,
    )
    async def get_connection(request: Request, connection_id: UUID) -> InstagramConnectionResponse:
        owner_user_id = await dependencies.owner_context.require_owner_user_id(request)
        connection = await _execute_connection_read(
            dependencies=dependencies,
            owner_user_id=owner_user_id,
            connection_id=InstagramConnectionId(connection_id),
        )
        return dependencies.connection_mapper.map(connection)

    @router.post(
        "/instagram/connections/{connection_id}/disconnect",
        response_model=InstagramConnectionResponse,
    )
    async def disconnect_connection(
        request: Request,
        connection_id: UUID,
    ) -> InstagramConnectionResponse:
        owner_user_id = await dependencies.owner_context.require_owner_user_id(request)
        try:
            connection = await dependencies.disconnect_connection.execute(
                owner_user_id=owner_user_id,
                connection_id=InstagramConnectionId(connection_id),
            )
        except InstagramConnectionNotFoundError as exc:
            raise _not_found_http_exception() from exc
        except InstagramConnectionOwnershipError as exc:
            raise _forbidden_http_exception() from exc
        return dependencies.connection_mapper.map(connection)

    @router.post(
        "/instagram/connections/{connection_id}/reconnect",
        response_model=InstagramConnectionResponse,
    )
    async def reconnect_connection(
        request: Request,
        connection_id: UUID,
    ) -> InstagramConnectionResponse:
        owner_user_id = await dependencies.owner_context.require_owner_user_id(request)
        try:
            connection = await dependencies.reconnect_connection.execute(
                owner_user_id=owner_user_id,
                connection_id=InstagramConnectionId(connection_id),
            )
        except InstagramConnectionNotFoundError as exc:
            raise _not_found_http_exception() from exc
        except InstagramConnectionOwnershipError as exc:
            raise _forbidden_http_exception() from exc
        return dependencies.connection_mapper.map(connection)

    return router


async def _execute_connection_read(
    *,
    dependencies: InstagramFastApiDependencies,
    owner_user_id: str,
    connection_id: InstagramConnectionId,
) -> InstagramConnection:
    try:
        return await dependencies.get_connection.execute(
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
    except InstagramConnectionNotFoundError as exc:
        raise _not_found_http_exception() from exc
    except InstagramConnectionOwnershipError as exc:
        raise _forbidden_http_exception() from exc


def _not_found_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Instagram connection not found",
    )


def _forbidden_http_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Instagram connection access denied",
    )
