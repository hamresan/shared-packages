from customer.domain.external_identity import (
    CustomerExternalIdentity,
    ExternalIdentityKey,
    ExternalIdentityStatus,
)
from customer.infrastructure.persistence.sqlalchemy.models import CustomerExternalIdentityModel


class ExternalIdentityMapper:
    @staticmethod
    def to_domain(row: CustomerExternalIdentityModel) -> CustomerExternalIdentity:
        return CustomerExternalIdentity(
            id=row.id,
            key=ExternalIdentityKey(
                business_id=row.business_id,
                provider=row.provider,
                channel_account_id=row.channel_account_id,
                external_user_id=row.external_user_id,
            ),
            customer_id=row.customer_id,
            status=ExternalIdentityStatus(row.status),
            linked_at=row.linked_at,
            verification_method=row.verification_method,
            verified_at=row.verified_at,
            revoked_at=row.revoked_at,
        )

    @staticmethod
    def to_row(value: CustomerExternalIdentity) -> CustomerExternalIdentityModel:
        return CustomerExternalIdentityModel(
            id=value.id,
            business_id=value.key.business_id,
            customer_id=value.customer_id,
            provider=value.key.provider,
            channel_account_id=value.key.channel_account_id,
            external_user_id=value.key.external_user_id,
            status=value.status.value,
            linked_at=value.linked_at,
            verification_method=value.verification_method,
            verified_at=value.verified_at,
            revoked_at=value.revoked_at,
        )
