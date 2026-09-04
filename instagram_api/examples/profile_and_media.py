"""Read one connected Instagram profile and its media through the package."""

import asyncio
import os

from instagram_api.application.accounts import (
    InstagramAccountAccessPolicy,
    InstagramAccountService,
)
from instagram_api.application.contracts import (
    InstagramAccessTokenProvider,
    InstagramConnectionReader,
)
from instagram_api.application.media import InstagramMediaAccessPolicy, InstagramMediaService
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
)
from instagram_api.infrastructure.meta.accounts import (
    MetaInstagramAccountMapper,
    MetaInstagramAccountPayloadParser,
    MetaInstagramAccountProvider,
)
from instagram_api.infrastructure.meta.http import (
    HttpxMetaHttpTransport,
    MetaApiConfig,
    MetaErrorDecoder,
    MetaPaginationCursorMapper,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    MetaTimeoutConfig,
    NullMetaHttpObserver,
)
from instagram_api.infrastructure.meta.media import (
    MetaInstagramMediaErrorMapper,
    MetaInstagramMediaFieldParser,
    MetaInstagramMediaMapper,
    MetaInstagramMediaPayloadParser,
    MetaInstagramMediaProvider,
    MetaInstagramMediaTimestampParser,
    MetaInstagramMediaTypeMapper,
)

BASIC_PERMISSION = "instagram_business_basic"


class ExampleConnectionReader(InstagramConnectionReader):
    """Example host adapter for one already-authorized Instagram connection."""

    def __init__(
        self,
        connection_id: InstagramConnectionId,
        provider_account_id: InstagramAccountId,
    ) -> None:
        self._connection = InstagramConnection(
            id=connection_id,
            provider_account_id=provider_account_id,
            permissions=frozenset({BASIC_PERMISSION}),
            is_usable=True,
        )

    async def get_connection(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        if connection_id != self._connection.id:
            raise LookupError(f"Unknown Instagram connection: {connection_id}")
        return self._connection


class EnvironmentAccessTokenProvider(InstagramAccessTokenProvider):
    """Example host adapter that supplies the selected connection's access token."""

    def __init__(
        self,
        connection_id: InstagramConnectionId,
        access_token: str,
    ) -> None:
        self._connection_id = connection_id
        self._access_token = access_token

    async def get_access_token(self, connection_id: InstagramConnectionId) -> str:
        if connection_id != self._connection_id:
            raise LookupError(f"No access token for connection: {connection_id}")
        return self._access_token


async def main() -> None:
    """Compose the package and read profile/media for one explicit connection."""

    connection_id = InstagramConnectionId(os.environ["INSTAGRAM_CONNECTION_ID"])
    provider_account_id = InstagramAccountId(os.environ["INSTAGRAM_ACCOUNT_ID"])
    api_version = os.environ["META_API_VERSION"]
    access_token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    connection_reader = ExampleConnectionReader(
        connection_id=connection_id,
        provider_account_id=provider_account_id,
    )
    access_token_provider = EnvironmentAccessTokenProvider(
        connection_id=connection_id,
        access_token=access_token,
    )

    request_builder = MetaRequestBuilder(
        MetaApiConfig(api_version=api_version),
        access_token_provider,
    )
    transport = HttpxMetaHttpTransport(MetaTimeoutConfig())
    executor = MetaRequestExecutor(
        request_builder,
        transport,
        MetaResponseDecoder(MetaErrorDecoder()),
        MetaRetryPolicy(),
        NullMetaHttpObserver(),
    )

    account_provider = MetaInstagramAccountProvider(
        executor,
        MetaInstagramAccountPayloadParser(),
        MetaInstagramAccountMapper(),
    )
    account_service = InstagramAccountService(
        connection_reader,
        account_provider,
        InstagramAccountAccessPolicy(),
    )

    media_provider = MetaInstagramMediaProvider(
        executor,
        MetaInstagramMediaPayloadParser(MetaInstagramMediaFieldParser()),
        MetaInstagramMediaMapper(
            MetaInstagramMediaTypeMapper(),
            MetaInstagramMediaTimestampParser(),
        ),
        MetaPaginationCursorMapper(),
        MetaInstagramMediaErrorMapper(),
    )
    media_service = InstagramMediaService(
        connection_reader,
        media_provider,
        InstagramMediaAccessPolicy(),
    )

    account = await account_service.get_account(connection_id)
    media_page = await media_service.list_media(connection_id)

    print(f"@{account.username}: {account.biography or ''}")
    for media in media_page.items:
        print(f"{media.media_type.value}: {media.caption or ''}")


if __name__ == "__main__":
    asyncio.run(main())
