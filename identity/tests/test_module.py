from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from identity.infrastructure.persistence.sqlalchemy import SqlAlchemyIdentityUnitOfWork
from identity.module import IdentityModule, IdentityModuleConfig
from identity.presentation.fastapi import FastApiIdentityAdapter
from tests.support import FakeAccessTokenAuthenticator


@asynccontextmanager
async def unused_session_factory() -> AsyncGenerator[AsyncSession]:
    raise AssertionError("Session factory should not be opened while testing module wiring")
    yield  # pragma: no cover


def test_identity_module_wires_public_components() -> None:
    authenticator = FakeAccessTokenAuthenticator()
    module = IdentityModule(
        IdentityModuleConfig(
            session_factory=unused_session_factory,
            access_token_authenticator=authenticator,
        )
    )

    assert isinstance(module.unit_of_work, SqlAlchemyIdentityUnitOfWork)
    assert module.public_api.access_token_authenticator is authenticator
    assert isinstance(module.fastapi, FastApiIdentityAdapter)
    assert module.fastapi.access_token_authenticator is authenticator
