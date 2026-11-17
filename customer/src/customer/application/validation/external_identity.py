from customer.application.contracts.external_identity_evidence import (
    VerifiedExternalIdentityEvidence,
)
from customer.domain.errors import CustomerIdentityVerificationError, CustomerValidationError
from customer.domain.external_identity import (
    CustomerExternalIdentity,
    ExternalIdentityKey,
    ExternalIdentityStatus,
)


class ExternalIdentityKeyValidator:
    def normalize(self, key: ExternalIdentityKey) -> ExternalIdentityKey:
        provider = key.provider.strip().lower()
        account = key.channel_account_id.strip()
        subject = key.external_user_id.strip()
        if not (1 <= len(provider) <= 40 and provider.replace("_", "").isalnum()):
            raise CustomerValidationError("Invalid identity provider")
        if not (1 <= len(account) <= 200 and 1 <= len(subject) <= 200):
            raise CustomerValidationError("Invalid external identity namespace")
        return ExternalIdentityKey(key.business_id, provider, account, subject)


class ExternalIdentityEvidencePolicy:
    def require_matching(
        self, key: ExternalIdentityKey, evidence: VerifiedExternalIdentityEvidence
    ) -> None:
        if evidence.key != key:
            raise CustomerIdentityVerificationError("Evidence does not match external identity")
        if not evidence.method or not evidence.method.strip():
            raise CustomerIdentityVerificationError("Missing verification method")
        if evidence.verified_at.tzinfo is None or evidence.verified_at.utcoffset() is None:
            raise CustomerIdentityVerificationError("Verification time must be timezone-aware")

    def require_after_revocation(
        self, previous: CustomerExternalIdentity | None, evidence: VerifiedExternalIdentityEvidence
    ) -> None:
        if previous is None or previous.status is not ExternalIdentityStatus.REVOKED:
            return
        if previous.revoked_at is None or evidence.verified_at <= previous.revoked_at:
            raise CustomerIdentityVerificationError("Relinking requires proof after revocation")
