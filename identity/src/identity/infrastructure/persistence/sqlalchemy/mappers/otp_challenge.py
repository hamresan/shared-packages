from identity.domain import OtpChallenge
from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper
from identity.infrastructure.persistence.sqlalchemy.models import OtpChallengeModel


class OtpChallengeMapper:
    def __init__(self, datetime_mapper: UtcDateTimeMapper | None = None) -> None:
        self._datetime_mapper = datetime_mapper or UtcDateTimeMapper()

    def to_domain(self, model: OtpChallengeModel) -> OtpChallenge:
        return OtpChallenge(
            id=model.id,
            user_id=model.user_id,
            identity_id=model.identity_id,
            identifier_type=model.identifier_type,
            normalized_destination=model.normalized_destination,
            destination_snapshot=model.destination_snapshot,
            purpose=model.purpose,
            code_hash=model.code_hash,
            expires_at=self._datetime_mapper.to_domain(model.expires_at),
            resend_available_at=self._datetime_mapper.to_domain(model.resend_available_at),
            attempts_count=model.attempts_count,
            max_attempts=model.max_attempts,
            verified_at=self._datetime_mapper.to_domain_optional(model.verified_at),
            consumed_at=self._datetime_mapper.to_domain_optional(model.consumed_at),
            created_at=self._datetime_mapper.to_domain(model.created_at),
        )

    def to_model(self, entity: OtpChallenge) -> OtpChallengeModel:
        return OtpChallengeModel(
            id=entity.id,
            user_id=entity.user_id,
            identity_id=entity.identity_id,
            identifier_type=entity.identifier_type,
            normalized_destination=entity.normalized_destination,
            destination_snapshot=entity.destination_snapshot,
            purpose=entity.purpose,
            code_hash=entity.code_hash,
            expires_at=entity.expires_at,
            resend_available_at=entity.resend_available_at,
            attempts_count=entity.attempts_count,
            max_attempts=entity.max_attempts,
            verified_at=entity.verified_at,
            consumed_at=entity.consumed_at,
            created_at=entity.created_at,
        )
