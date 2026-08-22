"""FastAPI integration authentication dependency."""

from fastapi import Request

from integration_auth.application.errors.authentication import IntegrationAuthenticationError
from integration_auth.application.errors.replay import ReplayProtectionError
from integration_auth.application.services.authentication.authenticate_integration_request import (
    AuthenticateIntegrationRequestService,
)
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.presentation.errors.http_error_mapper import FastApiIntegrationErrorMapper
from integration_auth.presentation.mappers.authentication_request_mapper import (
    FastApiAuthenticationRequestMapper,
)
from integration_auth.presentation.mappers.signed_request_header_parser import SignedRequestHeaderParser
from integration_auth.presentation.validators.required_header_reader import (
    InvalidSignedRequestHeadersError,
)


class IntegrationAuthenticationDependency:
    """Authenticate one FastAPI request and return its integration principal."""

    def __init__(
        self,
        *,
        authenticator: AuthenticateIntegrationRequestService,
        header_parser: SignedRequestHeaderParser,
        request_mapper: FastApiAuthenticationRequestMapper,
        error_mapper: FastApiIntegrationErrorMapper,
    ) -> None:
        self._authenticator = authenticator
        self._header_parser = header_parser
        self._request_mapper = request_mapper
        self._error_mapper = error_mapper

    async def __call__(self, request: Request) -> IntegrationPrincipal:
        try:
            headers = self._header_parser.parse(request)
            authentication_request = await self._request_mapper.map(request, headers)
            return await self._authenticator.authenticate(authentication_request)
        except (
            IntegrationAuthenticationError,
            ReplayProtectionError,
            InvalidSignedRequestHeadersError,
            ValueError,
        ) as exc:
            raise self._error_mapper.authentication_error() from exc
