"""Meta Instagram OAuth HTTP client."""

from instagram_auth.application.errors import InstagramProviderError
from instagram_auth.baseline import InstagramProviderErrorKind

from .config import MetaInstagramOAuthConfig
from .dto import MetaInstagramIdentityDto, MetaInstagramTokenDto
from .http import MetaHttpTransport, MetaTransportError, MetaTransportTimeoutError
from .mappers import MetaProviderErrorMapper


class MetaInstagramOAuthClient:
    """Own Meta-specific OAuth endpoints and response validation."""

    def __init__(
        self,
        transport: MetaHttpTransport,
        config: MetaInstagramOAuthConfig,
        error_mapper: MetaProviderErrorMapper,
    ) -> None:
        self._transport = transport
        self._config = config
        self._error_mapper = error_mapper

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
        return self._parse_token(response.payload)

    async def resolve_identity(self, *, access_token: str) -> MetaInstagramIdentityDto:
        url = f"{self._config.graph_base_url}/{self._config.graph_api_version}/me"
        for attempt in range(2):
            try:
                response = await self._transport.get(
                    url=url,
                    params={
                        "fields": "user_id,username,account_type",
                        "access_token": access_token,
                    },
                )
            except MetaTransportTimeoutError as exc:
                if attempt == 0:
                    continue
                raise self._error_mapper.timeout_error() from exc
            except MetaTransportError as exc:
                if attempt == 0:
                    continue
                raise self._error_mapper.transport_error() from exc
            if response.status_code >= 500 and attempt == 0:
                continue
            if response.status_code != 200:
                raise self._error_mapper.identity_error(response)
            return self._parse_identity(response.payload)
        raise InstagramProviderError(
            kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
            message="Instagram provider error: unexpected_provider_error",
        )

    @staticmethod
    def _parse_token(payload: dict[str, object]) -> MetaInstagramTokenDto:
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in")
        if not isinstance(access_token, str) or not access_token:
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        if expires_in is not None and not isinstance(expires_in, int):
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        return MetaInstagramTokenDto(access_token=access_token, expires_in=expires_in)

    @staticmethod
    def _parse_identity(payload: dict[str, object]) -> MetaInstagramIdentityDto:
        user_id = payload.get("user_id")
        username = payload.get("username")
        account_type = payload.get("account_type")
        if not all(isinstance(value, str) and value for value in (user_id, username, account_type)):
            raise InstagramProviderError(
                kind=InstagramProviderErrorKind.UNEXPECTED_PROVIDER_ERROR,
                message="Instagram provider error: unexpected_provider_error",
            )
        return MetaInstagramIdentityDto(
            user_id=user_id,
            username=username,
            account_type=account_type,
        )
