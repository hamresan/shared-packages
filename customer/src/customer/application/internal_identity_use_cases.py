from dataclasses import dataclass

from customer.application.services.link_internal_identity import LinkInternalIdentityService
from customer.application.services.resolve_internal_identity import ResolveInternalIdentityService
from customer.application.services.unlink_internal_identity import UnlinkInternalIdentityService


@dataclass(frozen=True, slots=True)
class InternalIdentityUseCases:
    link: LinkInternalIdentityService
    unlink: UnlinkInternalIdentityService
    resolve: ResolveInternalIdentityService
