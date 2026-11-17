from datetime import UTC, datetime

from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
    VerifiedExternalIdentityEvidence,
)
from customer.domain.errors import CustomerIdentityVerificationError
from customer.domain.external_identity import ExternalIdentityKey


class FakeExternalEvidenceVerifier(ExternalIdentityEvidenceVerifier):
    def __init__(self) -> None:
        self.accepted: dict[str, VerifiedExternalIdentityEvidence] = {}

    def register(
        self,
        reference: str,
        key: ExternalIdentityKey,
        method: str = "provider_assertion",
        verified_at: datetime | None = None,
    ) -> None:
        self.accepted[reference] = VerifiedExternalIdentityEvidence(
            key, method, verified_at or datetime(2026, 1, 1, tzinfo=UTC)
        )

    async def require_verified(
        self, key: ExternalIdentityKey, evidence_reference: str
    ) -> VerifiedExternalIdentityEvidence:
        evidence = self.accepted.get(evidence_reference)
        if evidence is None:
            raise CustomerIdentityVerificationError("Untrusted verification evidence")
        return evidence
