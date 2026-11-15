from business.application.branch_access import BranchBusinessAccess, BranchScopePolicy
from business.application.branch_validators import (
    BranchAddressValidator,
    BranchContactValidator,
    BranchDetailsValidator,
    CreateBranchCommandValidator,
    ListBranchesQueryValidator,
    UpdateBranchCommandValidator,
)
from business.application.contracts import BusinessUnitOfWorkFactory, Clock, IdentifierGenerator
from business.application.factories import BranchFactory, BusinessFactory, OwnerMembershipFactory
from business.application.membership_access import (
    MembershipBranchVisibility,
    MembershipManagementAccess,
)
from business.application.membership_auditor import MembershipAuditor
from business.application.policies import BusinessAccessPolicy
from business.application.services import (
    AcceptMembershipService,
    ArchiveBranchService,
    ArchiveBusinessService,
    ChangeMemberRoleService,
    CreateBranchService,
    CreateBusinessService,
    GetBranchService,
    GetBusinessService,
    InviteMemberService,
    ListBranchesService,
    ListBusinessesService,
    ListMembershipsService,
    ReactivateBranchService,
    RevokeMembershipService,
    SetMemberBranchAccessService,
    TransferOwnershipService,
    UpdateBranchService,
    UpdateBusinessService,
)
from business.application.validators import (
    BusinessProfileValidator,
    CreateBusinessCommandValidator,
    UpdateBusinessCommandValidator,
)
from business.domain.validators import (
    BranchNameValidator,
    BusinessNameValidator,
    BusinessTypeValidator,
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageCodeValidator,
    OptionalTextValidator,
    TimeZoneValidator,
)
from business.presentation.dependencies import BranchUseCases, BusinessUseCases, MembershipUseCases


class BusinessApplicationFactory:
    """Composition root for framework-independent business use cases."""

    def __init__(
        self, uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._ids = ids

    def businesses(self) -> BusinessUseCases:
        profile = BusinessProfileValidator(BusinessNameValidator(), BusinessTypeValidator())
        return BusinessUseCases(
            create=CreateBusinessService(
                self._uow,
                CreateBusinessCommandValidator(
                    profile,
                    CountryCodeValidator(),
                    LanguageCodeValidator(),
                    CurrencyCodeValidator(),
                ),
                BusinessFactory(self._ids),
                OwnerMembershipFactory(self._ids),
                self._clock,
            ),
            get=GetBusinessService(self._uow, BusinessAccessPolicy()),
            list=ListBusinessesService(self._uow),
            update=UpdateBusinessService(
                self._uow,
                BusinessAccessPolicy(),
                UpdateBusinessCommandValidator(profile),
                self._clock,
            ),
            archive=ArchiveBusinessService(self._uow, BusinessAccessPolicy(), self._clock),
        )

    def branches(self) -> BranchUseCases:
        access = BranchBusinessAccess(BusinessAccessPolicy())
        scope = BranchScopePolicy()
        details = BranchDetailsValidator(
            BranchNameValidator(),
            TimeZoneValidator(),
            BranchAddressValidator(CountryCodeValidator(), OptionalTextValidator()),
            BranchContactValidator(OptionalTextValidator()),
        )
        visibility = MembershipBranchVisibility()
        return BranchUseCases(
            create=CreateBranchService(
                self._uow,
                access,
                CreateBranchCommandValidator(details),
                BranchFactory(self._ids),
                self._clock,
            ),
            get=GetBranchService(self._uow, access, scope, visibility),
            list=ListBranchesService(
                self._uow,
                access,
                ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator()),
                visibility,
            ),
            update=UpdateBranchService(
                self._uow, access, scope, UpdateBranchCommandValidator(details), self._clock
            ),
            archive=ArchiveBranchService(self._uow, access, scope, self._clock),
            reactivate=ReactivateBranchService(self._uow, access, scope, self._clock),
        )

    def memberships(self) -> MembershipUseCases:
        access = MembershipManagementAccess(BusinessAccessPolicy())
        auditor = MembershipAuditor(self._clock, self._ids)
        return MembershipUseCases(
            invite=InviteMemberService(self._uow, access, self._clock, self._ids, auditor),
            accept=AcceptMembershipService(self._uow, self._clock, auditor),
            list=ListMembershipsService(self._uow, access),
            change_role=ChangeMemberRoleService(self._uow, access, self._clock, auditor),
            revoke=RevokeMembershipService(self._uow, access, self._clock, auditor),
            set_access=SetMemberBranchAccessService(self._uow, access, self._clock, auditor),
            transfer=TransferOwnershipService(self._uow, access, self._clock, auditor),
        )
