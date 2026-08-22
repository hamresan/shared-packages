"""Composition factory for the FastAPI integration-auth adapter."""

from dataclasses import dataclass

from integration_auth.application.contracts.crypto.body_hasher import BodyHasher
from integration_auth.application.services.authentication.authenticate_integration_request import (
    AuthenticateIntegrationRequestService,
)
from integration_auth.application.services.authorization.integration_authorizer import (
    IntegrationAuthorizer,
)
from integration_auth.presentation.dependencies.authentication import (
    IntegrationAuthenticationDependency,
)
from integration_auth.presentation.dependencies.authorization import (
    IntegrationPermissionDependencyFactory,
)
from integration_auth.presentation.errors.http_error_mapper import FastApiIntegrationErrorMapper
from integration_auth.presentation.mappers.authentication_request_mapper import (
    FastApiAuthenticationRequestMapper,
)
from integration_auth.presentation.mappers.signed_request_header_parser import SignedRequestHeaderParser
from integration_auth.presentation.validators.required_header_reader import RequiredHeaderReader
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder


@dataclass(frozen=True, slots=True)
class FastApiIntegrationAuth:
    """FastAPI authentication and authorization dependency surfaces."""

    authenticate: IntegrationAuthenticationDependency
    permissions: IntegrationPermissionDependencyFactory


class FastApiIntegrationAuthFactory:
    """Compose presentation components from application and protocol dependencies."""

    def create(
        self,
        *,
        authenticator: AuthenticateIntegrationRequestService,
        authorizer: IntegrationAuthorizer,
        body_hasher: BodyHasher,
        query_encoder: CanonicalQueryEncoder,
    ) -> FastApiIntegrationAuth:
        error_mapper = FastApiIntegrationErrorMapper()
        authentication_dependency = IntegrationAuthenticationDependency(
            authenticator=authenticator,
            header_parser=SignedRequestHeaderParser(RequiredHeaderReader()),
            request_mapper=FastApiAuthenticationRequestMapper(
                body_hasher=body_hasher,
                query_encoder=query_encoder,
            ),
            error_mapper=error_mapper,
        )
        return FastApiIntegrationAuth(
            authenticate=authentication_dependency,
            permissions=IntegrationPermissionDependencyFactory(
                authorizer=authorizer,
                authentication_dependency=authentication_dependency,
                error_mapper=error_mapper,
            ),
        )
