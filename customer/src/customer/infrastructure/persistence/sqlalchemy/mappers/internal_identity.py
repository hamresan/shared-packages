from customer.domain.identity_link import CustomerIdentityLink
from customer.infrastructure.persistence.sqlalchemy.models import CustomerIdentityLinkModel


class InternalIdentityMapper:
    @staticmethod
    def to_domain(row: CustomerIdentityLinkModel) -> CustomerIdentityLink:
        return CustomerIdentityLink(
            id=row.id,
            business_id=row.business_id,
            customer_id=row.customer_id,
            identity_user_id=row.identity_user_id,
            linked_at=row.linked_at,
            revoked_at=row.revoked_at,
        )

    @staticmethod
    def to_row(value: CustomerIdentityLink) -> CustomerIdentityLinkModel:
        return CustomerIdentityLinkModel(
            id=value.id,
            business_id=value.business_id,
            customer_id=value.customer_id,
            identity_user_id=value.identity_user_id,
            linked_at=value.linked_at,
            revoked_at=value.revoked_at,
        )
