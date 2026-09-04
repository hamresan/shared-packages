"""Connection-aware Meta request construction."""

from typing import Mapping

from instagram_api.application.contracts.connection import InstagramAccessTokenProvider
from instagram_api.domain import InstagramConnectionId

from .config import MetaApiConfig
from .models import MetaHttpMethod, MetaHttpRequest


class MetaRequestBuilder:
    """Builds authenticated versioned Meta requests for an explicit connection."""

    def __init__(
        self,
        config: MetaApiConfig,
        access_token_provider: InstagramAccessTokenProvider,
    ) -> None:
        self._config = config
        self._access_token_provider = access_token_provider

    async def build(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: MetaHttpMethod,
        path: str,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> MetaHttpRequest:
        """Build one authenticated request for the selected connection."""

        access_token = await self._access_token_provider.get_access_token(connection_id)
        return MetaHttpRequest(
            method=method,
            url=self._config.build_url(path),
            headers={"Authorization": f"Bearer {access_token}"},
            params=params or {},
            json_body=json_body,
        )
