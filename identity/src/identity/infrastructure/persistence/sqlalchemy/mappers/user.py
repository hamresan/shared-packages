from identity.domain import User
from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserModel


class UserMapper:
    def __init__(self, datetime_mapper: UtcDateTimeMapper | None = None) -> None:
        self._datetime_mapper = datetime_mapper or UtcDateTimeMapper()

    def to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            full_name=model.full_name,
            status=model.status,
            created_at=self._datetime_mapper.to_domain(model.created_at),
            updated_at=self._datetime_mapper.to_domain(model.updated_at),
        )

    def to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            full_name=entity.full_name,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
