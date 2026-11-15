from business.application.contracts import BusinessUnitOfWorkFactory, Clock, IdentifierGenerator
from business.application.factories import BusinessFactory, OwnerMembershipFactory
from business.application.policies import BusinessAccessPolicy
from business.application.services import (
    ArchiveBusinessService,
    CreateBusinessService,
    GetBusinessService,
    ListBusinessesService,
    UpdateBusinessService,
)
from business.application.validators import (
    BusinessProfileValidator,
    CreateBusinessCommandValidator,
    UpdateBusinessCommandValidator,
)
from business.domain.validators import (
    BusinessNameValidator,
    BusinessTypeValidator,
    CountryCodeValidator,
    CurrencyCodeValidator,
    LanguageCodeValidator,
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
