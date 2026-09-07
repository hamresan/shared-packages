"""Automatic Instagram credential refresh for downstream API access."""

from collections.abc import Collection
from dataclasses import replace
from datetime import datetime, timedelta

from instagram_auth.application.contracts.access_token_provider import InstagramAccessTokenProvider
from instagram_auth.application.contracts.access_token_refresher import InstagramAccessTokenRefresher
from instagram_auth.application.contracts.clock import Clock
from instagram_auth.application.contracts.token_protector import InstagramAccessTokenProtector
from instagram_auth.application.contracts.unit_of_work import InstagramAuthUnitOfWork
from instagram_auth.application.credentials.factory import InstagramProtectedCredentialFactory
from instagram_auth.application.errors import InstagramConnectionUnavailableError
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId


class InstagramCredentialRefreshPolicy:
    """Decide whether a still-valid credential should be refreshed now."""

    def __init__(self, refresh_before_expiry: timedelta) -> None:
        self._refresh_before_expiry = refresh_before_expiry

    def should_refresh(self, *, expires_at: datetime | None, now: datetime) -> bool:
        if expires_at is None or expires_at <= now:
            return False
        return expires_at <= now + self._refresh_before_expiry


class RefreshInstagramConnectionCredential:
    """Refresh and persist one connection credential when it nears expiry."""

    def __init__(
        self,
        *,
        unit_of_work: InstagramAuthUnitOfWork,
        token_refresher: InstagramAccessTokenRefresher,
        token_protector: InstagramAccessTokenProtector,
        credential_factory: InstagramProtectedCredentialFactory,
        refresh_policy: InstagramCredentialRefreshPolicy,
        clock: Clock,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._token_refresher = token_refresher
        self._token_protector = token_protector
        self._credential_factory = credential_factory
        self._refresh_policy = refresh_policy
        self._clock = clock

    async def execute(self, *, connection_id: InstagramConnectionId) -> bool:
        now = self._clock.now()
        async with self._unit_of_work:
            connection = await self._unit_of_work.connections.get_by_id(connection_id)
            credential = await self._unit_of_work.credentials.get(connection_id)
            if connection is None or credential is None or credential.revoked_at is not None:
                raise InstagramConnectionUnavailableError("Instagram credential is unavailable")

            expires_at = connection.credential_expires_at or credential.expires_at
            if not self._refresh_policy.should_refresh(expires_at=expires_at, now=now):
                return False

            access_token = self._token_protector.unprotect(credential.protected_access_token)
            grant = await self._token_refresher.refresh_access_token(access_token=access_token)
            refreshed_credential = self._credential_factory.build(
                connection_id=connection_id,
                grant=grant,
            )
            refreshed_connection = replace(
                connection,
                credential_expires_at=grant.expires_at,
                revoked_at=None,
                last_validated_at=now,
            )
            await self._unit_of_work.credentials.save(refreshed_credential)
            await self._unit_of_work.connections.update(refreshed_connection)
            await self._unit_of_work.commit()
            return True


class RefreshingInstagramAccessTokenProvider(InstagramAccessTokenProvider):
    """Refresh near-expiry credentials before delegating authorized token access."""

    def __init__(
        self,
        *,
        delegate: InstagramAccessTokenProvider,
        credential_refresher: RefreshInstagramConnectionCredential,
    ) -> None:
        self._delegate = delegate
        self._credential_refresher = credential_refresher

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> str:
        await self._credential_refresher.execute(connection_id=connection_id)
        return await self._delegate.get_access_token(
            connection_id=connection_id,
            required_permissions=required_permissions,
        )
