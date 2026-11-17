from dataclasses import dataclass

from customer.application.services.find_external_identity import FindExternalIdentityService
from customer.application.services.get_or_create_external_identity import (
    GetOrCreateExternalIdentityService,
)
from customer.application.services.link_external_identity import LinkExternalIdentityService
from customer.application.services.record_external_verification import (
    RecordExternalVerificationService,
)
from customer.application.services.relink_external_identity import RelinkExternalIdentityService
from customer.application.services.revoke_external_identity import RevokeExternalIdentityService


@dataclass(frozen=True, slots=True)
class ExternalIdentityUseCases:
    find: FindExternalIdentityService
    get_or_create: GetOrCreateExternalIdentityService
    link: LinkExternalIdentityService
    revoke: RevokeExternalIdentityService
    relink: RelinkExternalIdentityService
    record_verification: RecordExternalVerificationService
