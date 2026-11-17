"""Trust boundary: only host adapters may attest control of external identities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from customer.domain.external_identity import ExternalIdentityKey


@dataclass(frozen=True, slots=True)
class VerifiedExternalIdentityEvidence:
    key: ExternalIdentityKey
    method: str
    verified_at: datetime


class ExternalIdentityEvidenceVerifier(Protocol):
    async def require_verified(
        self, key: ExternalIdentityKey, evidence_reference: str
    ) -> VerifiedExternalIdentityEvidence: ...
