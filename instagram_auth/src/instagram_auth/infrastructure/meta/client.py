"""Meta Instagram OAuth HTTP client."""

from .config import MetaInstagramOAuthConfig
from .dto import MetaInstagramIdentityDto, MetaInstagramTokenDto
from .http import MetaHttpTransport, MetaTransportError, MetaTransportTimeoutError
from .mappers import MetaProviderErrorMapper
from .parsers import MetaIdentityPayloadParser, MetaTokenPayloadParser
from .retry import MetaIdentityRetryPolicy


class MetaInstagramOAuthClient:
    """Own Meta-specific OAuth endpoints and transport orchestration."""

    def __init__(
        self,
        transport: MetaHttpTransport,
        config: MetaInstagramOAuthConfig,
        error_mapper: MetaProviderErrorMapper,
        token_parser: MetaTokenPayloadParser,
        identity_parser: MetaIdentityPayloadParser,
        identity_retry_policy: MetaIdentityRetryPolicy,
    ) -> None:
        self._transport = transport
        self._config = config
        self._error_mapper = error_mapper
        self._token_parser = token_parser
        self._identity_parser = identity_parser
        self._identity_retry_policy = identity_retry_policy

    async def exchange_authorization_code(
        self,
        *,
        authorization_code: str,
        redirect_uri: str,
    ) -> MetaInstagramTokenDto:
        try:
            response = await self._transport.post_form(
                url=self._config.token_endpoint,
                data={
                    "client_id": self._config.client_id,
                    "client_secret": self._config.client_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": authorization_code,
                },
            )
        except MetaTransportTimeoutError as exc:
            raise self._error_mapper.timeout_error() from exc
        except MetaTransportError as exc:
            raise self._error_mapper.transport_error() from exc
        if response.status_code != 200:
            raise self._error_mapper.token_exchange_error(response)
        return self._token_parser.parse(response.payload)

    async def resolve_identity(self, *, access_token: str) -> MetaInstagramIdentityDto:
        url = f"{self._config.graph_base_url}/{self._config.graph_api_version}/me"
        attempt = 1
        while True:
            try:
                response = await self._transport.get(
                    url=url,
                    params={
                        "fields": "user_id,username,account_type",
                        "access_token": access_token,
                    },
                )
            except MetaTransportTimeoutError as exc:
                if self._identity_retry_policy.should_retry_transport(attempt=attempt):
                    attempt += 1
                    continue
                raise self._error_mapper.timeout_error() from exc
            except MetaTransportError as exc:
                if self._identity_retry_policy.should_retry_transport(attempt=attempt):
                    attempt += 1
                    continue
                raise self._error_mapper.transport_error() from exc
            if self._identity_retry_policy.should_retry_status(
                status_code=response.status_code,
                attempt=attempt,
            ):
                attempt += 1
                continue
            if response.status_code != 200:
                raise self._error_mapper.identity_error(response)
            return self._identity_parser.parse(response.payload)
