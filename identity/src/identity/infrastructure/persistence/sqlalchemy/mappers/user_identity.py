from identity.domain import UserIdentity
from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper
from identity.infrastructure.persistence.sqlalchemy.models import UserIdentityModel


class UserIdentityMapper:
    def __init__(self, datetime_mapper: UtcDateTimeMapper | None = None) -> None:
        self._datetime_mapper = datetime_mapper or UtcDateTimeMapper()

    def to_domain(self, model: UserIdentityModel) -> UserIdentity:
        return UserIdentity(
            id=model.id,
            user_id=model.user_id,
            type=model.type,
            value=model.value,
            normalized_value=model.normalized_value,
            verified_at=self._datetime_mapper.to_domain_optional(model.verified_at),
            created_at=self._datetime_mapper.to_domain(model.created_at),
            updated_at=self._datetime_mapper.to_domain(model.updated_at),
        )

    def to_model(self, entity: UserIdentity) -> UserIdentityModel:
        return UserIdentityModel(
            id=entity.id,
            user_id=entity.user_id,
            type=entity.type,
            value=entity.value,
            normalized_value=entity.normalized_value,
            verified_at=entity.verified_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
