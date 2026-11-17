from dataclasses import dataclass
from uuid import UUID

from customer.application.actor import CustomerActor
from customer.domain.external_identity import ExternalIdentityKey


@dataclass(frozen=True, slots=True)
class FindExternalIdentityQuery:
    actor: CustomerActor
    key: ExternalIdentityKey


@dataclass(frozen=True, slots=True)
class LinkExternalIdentityCommand(FindExternalIdentityQuery):
    customer_id: UUID
    evidence_reference: str


@dataclass(frozen=True, slots=True)
class GetOrCreateExternalIdentityCommand(FindExternalIdentityQuery):
    evidence_reference: str
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class RevokeExternalIdentityCommand(FindExternalIdentityQuery):
    customer_id: UUID


@dataclass(frozen=True, slots=True)
class RecordExternalIdentityVerificationCommand(LinkExternalIdentityCommand):
    pass
