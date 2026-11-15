from business.application.actor import AuthenticatedActor
from business.application.contracts import BusinessUnitOfWorkFactory, Clock
from business.application.dto_membership import TransferOwnershipCommand
from business.application.membership_access import MembershipManagementAccess
from business.application.membership_auditor import MembershipAuditor
from business.domain.enums import MembershipAuditAction, MembershipStatus
from business.domain.errors import MembershipNotFoundError, OwnershipTransferError
from business.domain.membership import BusinessMembership


class TransferOwnershipService:
    def __init__(
        self,
        uow_factory: BusinessUnitOfWorkFactory,
        access: MembershipManagementAccess,
        clock: Clock,
        auditor: MembershipAuditor,
    ) -> None:
        self._uow_factory = uow_factory
        self._access = access
        self._clock = clock
        self._auditor = auditor

    async def execute(
        self, command: TransferOwnershipCommand, *, actor: AuthenticatedActor
    ) -> BusinessMembership:
        async with self._uow_factory() as uow:
            await self._access.require_owner(uow, command.business_id, actor)
            await uow.lock_business_membership(command.business_id)
            await self._access.require_owner(uow, command.business_id, actor)
            current = await uow.memberships.get_by_business_and_user(
                command.business_id, actor.user_id
            )
            recipient = await uow.memberships.get_for_business(
                command.business_id, command.recipient_membership_id
            )
            if current is None or recipient is None:
                raise MembershipNotFoundError("Ownership transfer membership was not found")
            if recipient.id == current.id or recipient.status is not MembershipStatus.ACTIVE:
                raise OwnershipTransferError("Recipient must be a different active business member")

            changed_at = self._clock.now()
            current.relinquish_ownership(changed_at=changed_at)
            recipient.assume_ownership(changed_at=changed_at)
            await uow.memberships.save(current)
            await uow.memberships.save(recipient)
            await uow.membership_branch_access.replace(recipient.id, ())
            await self._auditor.record(
                uow,
                current,
                actor.user_id,
                MembershipAuditAction.OWNERSHIP_TRANSFERRED,
                before=str(current.user_id),
                after=str(recipient.user_id),
            )
            await uow.commit()
            return recipient
