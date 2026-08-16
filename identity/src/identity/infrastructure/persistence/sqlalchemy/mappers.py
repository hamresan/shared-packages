from identity.domain import OtpChallenge, Session, User, UserIdentity
from identity.infrastructure.persistence.sqlalchemy.models import (
    OtpChallengeModel,
    SessionModel,
    UserIdentityModel,
    UserModel,
)


class UserMapper:
    def to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            full_name=model.full_name,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            full_name=entity.full_name,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class UserIdentityMapper:
    def to_domain(self, model: UserIdentityModel) -> UserIdentity:
        return UserIdentity(
            id=model.id,
            user_id=model.user_id,
            type=model.type,
            value=model.value,
            normalized_value=model.normalized_value,
            verified_at=model.verified_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
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


class OtpChallengeMapper:
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
            expires_at=model.expires_at,
            resend_available_at=model.resend_available_at,
            attempts_count=model.attempts_count,
            max_attempts=model.max_attempts,
            verified_at=model.verified_at,
            consumed_at=model.consumed_at,
            created_at=model.created_at,
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


class SessionMapper:
    def to_domain(self, model: SessionModel) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            refresh_token_hash=model.refresh_token_hash,
            family_id=model.family_id,
            parent_session_id=model.parent_session_id,
            replaced_by_session_id=model.replaced_by_session_id,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            device_info=model.device_info,
            ip_address=model.ip_address,
            created_at=model.created_at,
            last_used_at=model.last_used_at,
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
            revoked_at=entity.revoked_at,
            device_info=entity.device_info,
            ip_address=entity.ip_address,
            created_at=entity.created_at,
            last_used_at=entity.last_used_at,
        )
