"""Explicit dependency bundle for the optional FastAPI adapter."""

from dataclasses import dataclass

from instagram_auth.application.authorization.callback import ValidateInstagramAuthorizationCallback
from instagram_auth.application.authorization.start import StartInstagramAuthorization
from instagram_auth.application.connections.disconnect import DisconnectInstagramConnection
from instagram_auth.application.connections.get_connection import GetInstagramConnection
from instagram_auth.application.connections.list_connections import ListInstagramConnections
from instagram_auth.application.connections.reconnect import ReconnectInstagramConnection
from instagram_auth.application.connections.start_reauthorization import (
    StartInstagramConnectionReauthorization,
)

from .contracts import InstagramFastApiCallbackResponder, InstagramFastApiOwnerContext
from .errors import InstagramFastApiErrorMapper
from .mappers import InstagramConnectionResponseMapper


@dataclass(frozen=True, slots=True)
class InstagramFastApiDependencies:
    """All host/application dependencies required by the HTTP adapter."""

    start_authorization: StartInstagramAuthorization
    validate_callback: ValidateInstagramAuthorizationCallback
    list_connections: ListInstagramConnections
    get_connection: GetInstagramConnection
    disconnect_connection: DisconnectInstagramConnection
    reconnect_connection: ReconnectInstagramConnection
    start_connection_reauthorization: StartInstagramConnectionReauthorization
    owner_context: InstagramFastApiOwnerContext
    callback_responder: InstagramFastApiCallbackResponder
    connection_mapper: InstagramConnectionResponseMapper
    error_mapper: InstagramFastApiErrorMapper
