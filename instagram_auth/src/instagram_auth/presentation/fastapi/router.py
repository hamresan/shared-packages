"""Thin FastAPI routes over transport-independent Instagram auth use cases."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, Response

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
from instagram_auth.domain import InstagramConnectionId

from .config import InstagramFastApiConfig
from .dependencies import InstagramFastApiDependencies
from .schemas import InstagramAuthorizationStartResponse, InstagramConnectionResponse


class InstagramFastApiRouteHandlers:
    """HTTP handlers delegating all business behavior to injected boundaries."""

    def __init__(
        self,
        *,
        config: InstagramFastApiConfig,
        dependencies: InstagramFastApiDependencies,
    ) -> None:
        self._config = config
        self._dependencies = dependencies

    async def start_authorization(
        self,
        request: Request,
        flow: InstagramAuthorizationFlow = InstagramAuthorizationFlow.LOGIN,
        optional_permissions: Annotated[list[InstagramPermission] | None, Query()] = None,
    ) -> InstagramAuthorizationStartResponse:
        owner_user_id = None
        if flow is InstagramAuthorizationFlow.CONNECT_ACCOUNT:
            owner_user_id = await self._dependencies.owner_context.require_owner_user_id(request)

        result = await self._dependencies.start_authorization.execute(
            StartInstagramAuthorizationCommand(
                redirect_uri=self._config.redirect_uri,
                correlation=InstagramAuthorizationCorrelation(
                    flow=flow,
                    owner_user_id=owner_user_id,
                ),
                optional_permissions=optional_permissions or (),
            )
        )
        return InstagramAuthorizationStartResponse(
            authorization_url=result.authorization_url,
            expires_at=result.expires_at,
        )

    async def authorization_callback(
        self,
        request: Request,
        code: str,
        state_value: Annotated[str | None, Query(alias="state")] = None,
    ) -> Response:
        owner_user_id = await self._dependencies.owner_context.optional_owner_user_id(request)
        try:
            authorization = await self._dependencies.validate_callback.execute(
                state=state_value,
                redirect_uri=self._config.redirect_uri,
                authenticated_owner_user_id=owner_user_id,
            )
        except InstagramAuthorizationStateValidationError as exc:
            raise self._dependencies.error_mapper.authorization_callback(exc) from exc
        return await self._dependencies.callback_responder.respond(
            authorization_code=code,
            authorization=authorization,
        )

    async def list_connections(self, request: Request) -> list[InstagramConnectionResponse]:
        owner_user_id = await self._dependencies.owner_context.require_owner_user_id(request)
        connections = await self._dependencies.list_connections.execute(owner_user_id=owner_user_id)
        return [self._dependencies.connection_mapper.map(connection) for connection in connections]

    async def get_connection(
        self,
        request: Request,
        connection_id: UUID,
    ) -> InstagramConnectionResponse:
        owner_user_id = await self._dependencies.owner_context.require_owner_user_id(request)
        try:
            connection = await self._dependencies.get_connection.execute(
                owner_user_id=owner_user_id,
                connection_id=InstagramConnectionId(connection_id),
            )
        except (InstagramConnectionNotFoundError, InstagramConnectionOwnershipError) as exc:
            raise self._dependencies.error_mapper.connection_access(exc) from exc
        return self._dependencies.connection_mapper.map(connection)

    async def disconnect_connection(
        self,
        request: Request,
        connection_id: UUID,
    ) -> InstagramConnectionResponse:
        owner_user_id = await self._dependencies.owner_context.require_owner_user_id(request)
        try:
            connection = await self._dependencies.disconnect_connection.execute(
                owner_user_id=owner_user_id,
                connection_id=InstagramConnectionId(connection_id),
            )
        except (InstagramConnectionNotFoundError, InstagramConnectionOwnershipError) as exc:
            raise self._dependencies.error_mapper.connection_access(exc) from exc
        return self._dependencies.connection_mapper.map(connection)

    async def reconnect_connection(
        self,
        request: Request,
        connection_id: UUID,
    ) -> InstagramConnectionResponse:
        owner_user_id = await self._dependencies.owner_context.require_owner_user_id(request)
        try:
            connection = await self._dependencies.reconnect_connection.execute(
                owner_user_id=owner_user_id,
                connection_id=InstagramConnectionId(connection_id),
            )
        except (InstagramConnectionNotFoundError, InstagramConnectionOwnershipError) as exc:
            raise self._dependencies.error_mapper.connection_access(exc) from exc
        return self._dependencies.connection_mapper.map(connection)


def create_instagram_auth_router(
    *,
    config: InstagramFastApiConfig,
    dependencies: InstagramFastApiDependencies,
) -> APIRouter:
    """Create package routes without owning host prefixing or session behavior."""
    router = APIRouter()
    handlers = InstagramFastApiRouteHandlers(config=config, dependencies=dependencies)

    router.add_api_route(
        "/instagram/auth/start",
        handlers.start_authorization,
        methods=["GET"],
        response_model=InstagramAuthorizationStartResponse,
    )
    router.add_api_route(
        "/instagram/auth/callback",
        handlers.authorization_callback,
        methods=["GET"],
    )
    router.add_api_route(
        "/instagram/connections",
        handlers.list_connections,
        methods=["GET"],
        response_model=list[InstagramConnectionResponse],
    )
    router.add_api_route(
        "/instagram/connections/{connection_id}",
        handlers.get_connection,
        methods=["GET"],
        response_model=InstagramConnectionResponse,
    )
    router.add_api_route(
        "/instagram/connections/{connection_id}/disconnect",
        handlers.disconnect_connection,
        methods=["POST"],
        response_model=InstagramConnectionResponse,
    )
    router.add_api_route(
        "/instagram/connections/{connection_id}/reconnect",
        handlers.reconnect_connection,
        methods=["POST"],
        response_model=InstagramConnectionResponse,
    )
    return router
