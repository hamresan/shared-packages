from dataclasses import dataclass

from identity.application.contracts.database import AsyncSessionFactory
from identity.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyIdentityUnitOfWork
from identity.presentation.fastapi import FastApiIdentityAdapter
from identity.public import AccessTokenAuthenticator, IdentityPublicApi


@dataclass(frozen=True, slots=True)
class IdentityModuleConfig:
    session_factory: AsyncSessionFactory
    access_token_authenticator: AccessTokenAuthenticator


@dataclass(frozen=True, slots=True)
class IdentityModule:
    config: IdentityModuleConfig

    @property
    def unit_of_work(self) -> SqlAlchemyIdentityUnitOfWork:
        return SqlAlchemyIdentityUnitOfWork(self.config.session_factory)

    @property
    def public_api(self) -> IdentityPublicApi:
        return IdentityPublicApi(
            access_token_authenticator=self.config.access_token_authenticator,
        )

    @property
    def fastapi(self) -> FastApiIdentityAdapter:
        return FastApiIdentityAdapter(
            access_token_authenticator=self.config.access_token_authenticator,
        )
