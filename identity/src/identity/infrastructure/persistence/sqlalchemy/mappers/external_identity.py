from identity.domain import ExternalIdentity
from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper
from identity.infrastructure.persistence.sqlalchemy.models import ExternalIdentityModel


class ExternalIdentityMapper:
    def __init__(self, datetime_mapper: UtcDateTimeMapper | None = None) -> None:
        self._datetime_mapper = datetime_mapper or UtcDateTimeMapper()

    def to_domain(self, model: ExternalIdentityModel) -> ExternalIdentity:
        return ExternalIdentity(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            subject=model.subject,
            verified_at=self._datetime_mapper.to_domain(model.verified_at),
            created_at=self._datetime_mapper.to_domain(model.created_at),
            updated_at=self._datetime_mapper.to_domain(model.updated_at),
        )

    def to_model(self, entity: ExternalIdentity) -> ExternalIdentityModel:
        return ExternalIdentityModel(
            id=entity.id,
            user_id=entity.user_id,
            provider=entity.provider,
            subject=entity.subject,
            verified_at=entity.verified_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
