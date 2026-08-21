from identity.domain import Session
from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper
from identity.infrastructure.persistence.sqlalchemy.models import SessionModel


class SessionMapper:
    def __init__(self, datetime_mapper: UtcDateTimeMapper | None = None) -> None:
        self._datetime_mapper = datetime_mapper or UtcDateTimeMapper()

    def to_domain(self, model: SessionModel) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            refresh_token_hash=model.refresh_token_hash,
            family_id=model.family_id,
            parent_session_id=model.parent_session_id,
            replaced_by_session_id=model.replaced_by_session_id,
            expires_at=self._datetime_mapper.to_domain(model.expires_at),
            family_expires_at=self._datetime_mapper.to_domain(model.family_expires_at),
            revoked_at=self._datetime_mapper.to_domain_optional(model.revoked_at),
            device_info=model.device_info,
            ip_address=model.ip_address,
            created_at=self._datetime_mapper.to_domain(model.created_at),
            last_used_at=self._datetime_mapper.to_domain_optional(model.last_used_at),
        )

    def to_model(self, entity: Session) -> SessionModel:
        return SessionModel(
            id=entity.id,
            user_id=entity.user_id,
            refresh_token_hash=entity.refresh_token_hash,
            family_id=entity.family_id,
            parent_session_id=entity.parent_session_id,
            replaced_by_session_id=entity.replaced_by_session_id,
            expires_at=entity.expires_at,
            family_expires_at=entity.family_expires_at,
            revoked_at=entity.revoked_at,
            device_info=entity.device_info,
            ip_address=entity.ip_address,
            created_at=entity.created_at,
            last_used_at=entity.last_used_at,
        )
