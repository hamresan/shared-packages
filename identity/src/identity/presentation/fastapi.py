from dataclasses import dataclass, field
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from identity.application.errors import IdentityError
from identity.presentation.error_mapper import IdentityHttpErrorMapper
from identity.presentation.mappers import IdentityRequestMapper, IdentityResponseMapper
from identity.presentation.request_metadata import (
    DirectRequestMetadataResolver,
    RequestMetadataResolver,
)
from identity.presentation.schemas import (
    AuthSessionResponse,
    RefreshSessionRequest,
    RequestOtpRequest,
    RequestOtpResponse,
    RevokeSessionRequest,
    VerifyOtpRequest,
)
from identity.public import (
    AccessTokenAuthenticator,
    AuthenticatedPrincipal,
    OtpRequester,
    OtpVerifier,
    SessionRefresher,
    SessionRevoker,
)

bearer = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


@dataclass(frozen=True, slots=True)
class AuthenticatedUserDependency:
    access_token_authenticator: AccessTokenAuthenticator

    async def __call__(self, credentials: BearerCredentials) -> AuthenticatedPrincipal:
        if credentials is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        try:
            return await self.access_token_authenticator.authenticate(credentials.credentials)
        except Exception as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid authentication credentials",
            ) from exc


@dataclass(frozen=True, slots=True)
class CurrentUserEndpoint:
    async def __call__(self, principal: AuthenticatedPrincipal) -> dict[str, str]:
        return {"user_id": str(principal.user_id), "session_id": str(principal.session_id)}


@dataclass(frozen=True, slots=True)
class RequestOtpEndpoint:
    service: OtpRequester
    request_mapper: IdentityRequestMapper
    response_mapper: IdentityResponseMapper
    error_mapper: IdentityHttpErrorMapper

    async def __call__(self, request: RequestOtpRequest) -> RequestOtpResponse:
        try:
            result = await self.service.execute(self.request_mapper.to_request_otp_command(request))
        except IdentityError as error:
            raise self.error_mapper.to_http_exception(error) from error
        return self.response_mapper.from_request_otp_result(result)


@dataclass(frozen=True, slots=True)
class VerifyOtpEndpoint:
    service: OtpVerifier
    request_mapper: IdentityRequestMapper
    response_mapper: IdentityResponseMapper
    error_mapper: IdentityHttpErrorMapper
    metadata_resolver: RequestMetadataResolver

    async def __call__(self, payload: VerifyOtpRequest, request: Request) -> AuthSessionResponse:
        metadata = self.metadata_resolver.resolve(request)
        try:
            result = await self.service.execute(
                self.request_mapper.to_verify_otp_command(payload, metadata)
            )
        except IdentityError as error:
            raise self.error_mapper.to_http_exception(error) from error
        return self.response_mapper.from_auth_session_result(result)


@dataclass(frozen=True, slots=True)
class RefreshSessionEndpoint:
    service: SessionRefresher
    request_mapper: IdentityRequestMapper
    response_mapper: IdentityResponseMapper
    error_mapper: IdentityHttpErrorMapper
    metadata_resolver: RequestMetadataResolver

    async def __call__(self, payload: RefreshSessionRequest, request: Request) -> AuthSessionResponse:
        metadata = self.metadata_resolver.resolve(request)
        try:
            result = await self.service.execute(
                self.request_mapper.to_refresh_session_command(payload, metadata)
            )
        except IdentityError as error:
            raise self.error_mapper.to_http_exception(error) from error
        return self.response_mapper.from_auth_session_result(result)


@dataclass(frozen=True, slots=True)
class RevokeSessionEndpoint:
    service: SessionRevoker
    error_mapper: IdentityHttpErrorMapper

    async def __call__(self, request: RevokeSessionRequest) -> Response:
        try:
            await self.service.execute(request.refresh_token)
        except IdentityError as error:
            raise self.error_mapper.to_http_exception(error) from error
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@dataclass(frozen=True, slots=True)
class FastApiIdentityAdapter:
    access_token_authenticator: AccessTokenAuthenticator
    otp_requester: OtpRequester
    otp_verifier: OtpVerifier
    session_refresher: SessionRefresher
    session_revoker: SessionRevoker
    request_metadata_resolver: RequestMetadataResolver = field(
        default_factory=DirectRequestMetadataResolver
    )

    def router(self) -> APIRouter:
        request_mapper = IdentityRequestMapper()
        response_mapper = IdentityResponseMapper()
        error_mapper = IdentityHttpErrorMapper()
        authenticated_user = AuthenticatedUserDependency(self.access_token_authenticator)
        current_user = CurrentUserEndpoint()

        async def authenticated_current_user(
            principal: Annotated[AuthenticatedPrincipal, Depends(authenticated_user)],
        ) -> dict[str, str]:
            return await current_user(principal)

        router = APIRouter(prefix="/identity", tags=["identity"])
        router.add_api_route(
            "/otp/request",
            RequestOtpEndpoint(
                self.otp_requester,
                request_mapper,
                response_mapper,
                error_mapper,
            ),
            methods=["POST"],
            response_model=RequestOtpResponse,
            status_code=status.HTTP_202_ACCEPTED,
        )
        router.add_api_route(
            "/otp/verify",
            VerifyOtpEndpoint(
                self.otp_verifier,
                request_mapper,
                response_mapper,
                error_mapper,
                self.request_metadata_resolver,
            ),
            methods=["POST"],
            response_model=AuthSessionResponse,
        )
        router.add_api_route(
            "/sessions/refresh",
            RefreshSessionEndpoint(
                self.session_refresher,
                request_mapper,
                response_mapper,
                error_mapper,
                self.request_metadata_resolver,
            ),
            methods=["POST"],
            response_model=AuthSessionResponse,
        )
        router.add_api_route(
            "/sessions/revoke",
            RevokeSessionEndpoint(self.session_revoker, error_mapper),
            methods=["POST"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        router.add_api_route(
            "/me",
            authenticated_current_user,
            methods=["GET"],
            response_model=dict[str, str],
        )
        return router

    def install(self, app: FastAPI) -> None:
        app.include_router(self.router())
