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
    return GetBranchService(unit_of_work_factory, build_branch_access(), BranchScopePolicy())


def build_list_branch_service(
    unit_of_work_factory: BusinessUnitOfWorkFactory,
) -> ListBranchesService:
    return ListBranchesService(
        unit_of_work_factory,
        build_branch_access(),
        ListBranchesQueryValidator(CountryCodeValidator(), OptionalTextValidator()),
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
