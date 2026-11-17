from customer.application.models.identity_resolution import (
    CustomerResolution,
    InternalIdentityResolution,
)
from customer.domain.external_identity import CustomerExternalIdentity
from customer.domain.identity_link import CustomerIdentityLink


class IdentityResolutionMapper:
    def to_external(self, identity: CustomerExternalIdentity) -> CustomerResolution:
        return CustomerResolution(
            customer_id=identity.customer_id,
            business_id=identity.key.business_id,
            identity_status=identity.status,
            verification_method=identity.verification_method,
            verified_at=identity.verified_at,
        )

    def to_internal(self, link: CustomerIdentityLink) -> InternalIdentityResolution:
        return InternalIdentityResolution(
            customer_id=link.customer_id,
            business_id=link.business_id,
            identity_user_id=link.identity_user_id,
        )
