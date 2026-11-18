from business.application.authorization import BusinessAuthorizationService
from business.application.authorization.mapper import MembershipAuthorizationMapper
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
    ArchiveBranchService,
    ArchiveBusinessService,
    CreateBranchService,
    CreateBusinessService,
    GetBranchService,
    GetBusinessService,
    ListBranchesService,
    ListBusinessesService,
    ReactivateBranchService,
    UpdateBranchService,
    UpdateBusinessService,
)
from business.application.services.accept_membership import AcceptMembershipService
from business.application.services.change_member_role import ChangeMemberRoleService
from business.application.services.invite_member import InviteMemberService
from business.application.services.list_memberships import ListMembershipsService
from business.application.services.revoke_membership import RevokeMembershipService
from business.application.services.set_member_branch_access import SetMemberBranchAccessService
from business.application.services.transfer_ownership import TransferOwnershipService
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


def build_profile_validator() -> BusinessProfileValidator:
    return BusinessProfileValidator(BusinessNameValidator(), BusinessTypeValidator())


def build_create_validator() -> CreateBusinessCommandValidator:
    return CreateBusinessCommandValidator(
        profile_validator=build_profile_validator(),
        country_validator=CountryCodeValidator(),
        language_validator=LanguageCodeValidator(),
        currency_validator=CurrencyCodeValidator(),
    )


def build_create_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory,
    clock: Clock,
    identifier_generator: IdentifierGenerator,
) -> CreateBusinessService:
    return CreateBusinessService(
        unit_of_work_factory=unit_of_work_factory,
        validator=build_create_validator(),
        business_factory=BusinessFactory(identifier_generator),
        membership_factory=OwnerMembershipFactory(identifier_generator),
        clock=clock,
    )


def build_get_service(unit_of_work_factory: BusinessUnitOfWorkFactory) -> GetBusinessService:
    return GetBusinessService(unit_of_work_factory, BusinessAccessPolicy())


def build_list_service(unit_of_work_factory: BusinessUnitOfWorkFactory) -> ListBusinessesService:
    return ListBusinessesService(unit_of_work_factory)


def build_update_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory, clock: Clock
) -> UpdateBusinessService:
    return UpdateBusinessService(
        unit_of_work_factory,
        BusinessAccessPolicy(),
        UpdateBusinessCommandValidator(build_profile_validator()),
        clock,
    )


def build_archive_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory, clock: Clock
) -> ArchiveBusinessService:
    return ArchiveBusinessService(unit_of_work_factory, BusinessAccessPolicy(), clock)


def build_branch_details_validator() -> BranchDetailsValidator:
    return BranchDetailsValidator(
        name_validator=BranchNameValidator(),
        timezone_validator=TimeZoneValidator(),
        address_validator=BranchAddressValidator(CountryCodeValidator(), OptionalTextValidator()),
        contact_validator=BranchContactValidator(OptionalTextValidator()),
    )


def build_branch_access() -> BranchBusinessAccess:
    return BranchBusinessAccess(BusinessAccessPolicy())


def build_create_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory,
    clock: Clock,
    identifier_generator: IdentifierGenerator,
) -> CreateBranchService:
    return CreateBranchService(
        unit_of_work_factory,
        build_branch_access(),
        CreateBranchCommandValidator(build_branch_details_validator()),
        BranchFactory(identifier_generator),
        clock,
    )


def build_get_branch_service(unit_of_work_factory: BusinessUnitOfWorkFactory) -> GetBranchService:
    return GetBranchService(
        unit_of_work_factory,
        build_branch_access(),
        BranchScopePolicy(),
        MembershipBranchVisibility(),
    )


def build_list_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory,
) -> ListBranchesService:
    return ListBranchesService(
        unit_of_work_factory,
        build_branch_access(),
        ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator()),
        MembershipBranchVisibility(),
    )


def build_membership_access() -> MembershipManagementAccess:
    return MembershipManagementAccess(BusinessAccessPolicy())


def build_authorization_service(uow: BusinessUnitOfWorkFactory) -> BusinessAuthorizationService:
    return BusinessAuthorizationService(
        uow, BusinessAccessPolicy(), MembershipBranchVisibility(), MembershipAuthorizationMapper()
    )


def build_invite_member_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> InviteMemberService:
    return InviteMemberService(
        uow, build_membership_access(), clock, ids, MembershipAuditor(clock, ids)
    )


def build_accept_membership_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> AcceptMembershipService:
    return AcceptMembershipService(uow, clock, MembershipAuditor(clock, ids))


def build_change_member_role_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> ChangeMemberRoleService:
    return ChangeMemberRoleService(
        uow, build_membership_access(), clock, MembershipAuditor(clock, ids)
    )


def build_revoke_membership_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> RevokeMembershipService:
    return RevokeMembershipService(
        uow, build_membership_access(), clock, MembershipAuditor(clock, ids)
    )


def build_set_member_branch_access_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> SetMemberBranchAccessService:
    return SetMemberBranchAccessService(
        uow, build_membership_access(), clock, MembershipAuditor(clock, ids)
    )


def build_list_memberships_service(uow: BusinessUnitOfWorkFactory) -> ListMembershipsService:
    return ListMembershipsService(uow, build_membership_access())


def build_transfer_ownership_service(
    uow: BusinessUnitOfWorkFactory, clock: Clock, ids: IdentifierGenerator
) -> TransferOwnershipService:
    return TransferOwnershipService(
        uow, build_membership_access(), clock, MembershipAuditor(clock, ids)
    )


def build_update_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory, clock: Clock
) -> UpdateBranchService:
    return UpdateBranchService(
        unit_of_work_factory,
        build_branch_access(),
        BranchScopePolicy(),
        UpdateBranchCommandValidator(build_branch_details_validator()),
        clock,
    )


def build_archive_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory, clock: Clock
) -> ArchiveBranchService:
    return ArchiveBranchService(
        unit_of_work_factory, build_branch_access(), BranchScopePolicy(), clock
    )


def build_reactivate_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory, clock: Clock
) -> ReactivateBranchService:
    return ReactivateBranchService(
        unit_of_work_factory, build_branch_access(), BranchScopePolicy(), clock
    )
