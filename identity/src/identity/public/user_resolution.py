from identity.application.contracts.database import AsyncSessionFactory
from identity.application.errors import InvalidIdentityValueError
from identity.domain import IdentityType
from identity.infrastructure.persistence.sqlalchemy.mappers import UserIdentityMapper
from identity.infrastructure.persistence.sqlalchemy.repositories.user_identities import (
    SqlAlchemyUserIdentityRepository,
)
from identity.infrastructure.security.normalizer import DefaultIdentityNormalizer


class PublicIdentityUserResolver:
    """Resolve a registered user through a normalized public identity value."""

    def __init__(self, session_factory: AsyncSessionFactory) -> None:
        self._session_factory = session_factory
        self._normalizer = DefaultIdentityNormalizer()

    async def resolve_user_id(self, identity_type: IdentityType, value: str):
        try:
            normalized = self._normalizer.normalize(identity_type, value)
        except InvalidIdentityValueError:
            return None
        async with self._session_factory() as session:
            repository = SqlAlchemyUserIdentityRepository(session, UserIdentityMapper())
            identity = await repository.get_by_destination(identity_type, normalized)
        return identity.user_id if identity is not None else None
