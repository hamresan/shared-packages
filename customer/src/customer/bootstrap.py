"""Framework-independent Customer composition entry point."""

from dataclasses import dataclass

from customer.application.address_use_cases import AddressUseCases
from customer.application.contact_use_cases import ContactUseCases
from customer.application.contracts import (
    Clock,
    CustomerAuthorizer,
    CustomerCreationFingerprinter,
    CustomerUnitOfWorkFactory,
    IdentifierGenerator,
    IdentityVerifier,
)
from customer.application.customer_use_cases import CustomerUseCases
from customer.application.factories import CustomerFactory
from customer.application.mapping import CustomerResultMapper
from customer.application.mapping.address_result import AddressResultMapper
from customer.application.mapping.contact_result import ContactResultMapper
from customer.application.mapping.note_result import NoteResultMapper
from customer.application.mapping.preference_result import PreferenceResultMapper
from customer.application.note_use_cases import NoteUseCases
from customer.application.policies import CustomerScopePolicy
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.preference_use_cases import PreferenceUseCases
from customer.application.services import (
    ArchiveCustomerService,
    CreateCustomerService,
    GetCustomerService,
    ReactivateCustomerService,
    SearchCustomersService,
    UpdateCustomerService,
)
from customer.application.services.add_address import AddAddressService
from customer.application.services.add_contact import AddContactService
from customer.application.services.add_note import AddNoteService
from customer.application.services.list_addresses import ListAddressesService
from customer.application.services.list_contacts import ListContactsService
from customer.application.services.list_notes import ListNotesService
from customer.application.services.list_preferences import ListPreferencesService
from customer.application.services.remove_address import RemoveAddressService
from customer.application.services.remove_contact import RemoveContactService
from customer.application.services.remove_note import RemoveNoteService
from customer.application.services.remove_preference import RemovePreferenceService
from customer.application.services.set_default_address import SetDefaultAddressService
from customer.application.services.set_preference import SetPreferenceService
from customer.application.services.set_primary_contact import SetPrimaryContactService
from customer.application.services.update_address import UpdateAddressService
from customer.application.services.update_contact import UpdateContactService
from customer.application.validation import CustomerNameValidator, CustomerSearchValidator
from customer.application.validation.address import AddressValidator
from customer.application.validation.contact_value import ContactValueNormalizer
from customer.application.validation.note import NoteValidator
from customer.application.validation.preference import PreferenceValidator


@dataclass(frozen=True, slots=True)
class CustomerModuleConfig:
    """Host-supplied dependencies; no engine or provider is created here."""

    unit_of_work_factory: CustomerUnitOfWorkFactory
    authorizer: CustomerAuthorizer
    identity_verifier: IdentityVerifier
    clock: Clock
    identifiers: IdentifierGenerator
    creation_fingerprinter: CustomerCreationFingerprinter


class CustomerModule:
    """Stable public facade to which feature use cases are added by stage."""

    def __init__(self, config: CustomerModuleConfig) -> None:
        self._config = config
        scope = CustomerScopePolicy()
        mapper = CustomerResultMapper()
        names = CustomerNameValidator()
        contact_mapper = ContactResultMapper()
        contact_normalizer = ContactValueNormalizer()
        details_access = CustomerDetailAccessPolicy(scope, config.authorizer)
        address_validator = AddressValidator()
        preference_validator = PreferenceValidator()
        address_mapper = AddressResultMapper()
        preference_mapper = PreferenceResultMapper()
        note_mapper = NoteResultMapper()
        self._addresses = AddressUseCases(
            add=AddAddressService(
                config.unit_of_work_factory,
                details_access,
                address_validator,
                config.identifiers,
                address_mapper,
            ),
            list=ListAddressesService(config.unit_of_work_factory, details_access, address_mapper),
            update=UpdateAddressService(
                config.unit_of_work_factory, details_access, address_validator, address_mapper
            ),
            set_default=SetDefaultAddressService(
                config.unit_of_work_factory, details_access, address_mapper
            ),
            remove=RemoveAddressService(config.unit_of_work_factory, details_access),
        )
        self._preferences = PreferenceUseCases(
            set=SetPreferenceService(
                config.unit_of_work_factory,
                details_access,
                preference_validator,
                config.identifiers,
                preference_mapper,
            ),
            list=ListPreferencesService(
                config.unit_of_work_factory, details_access, preference_mapper
            ),
            remove=RemovePreferenceService(
                config.unit_of_work_factory, details_access, preference_validator
            ),
        )
        self._notes = NoteUseCases(
            add=AddNoteService(
                config.unit_of_work_factory,
                details_access,
                NoteValidator(),
                config.identifiers,
                config.clock,
                note_mapper,
            ),
            list=ListNotesService(config.unit_of_work_factory, details_access, note_mapper),
            remove=RemoveNoteService(config.unit_of_work_factory, details_access),
        )
        self._contacts = ContactUseCases(
            add=AddContactService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                contact_normalizer,
                config.identifiers,
                config.clock,
                contact_mapper,
            ),
            list=ListContactsService(
                config.unit_of_work_factory, config.authorizer, scope, contact_mapper
            ),
            update=UpdateContactService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                contact_normalizer,
                contact_mapper,
            ),
            set_primary=SetPrimaryContactService(
                config.unit_of_work_factory, config.authorizer, scope, contact_mapper
            ),
            remove=RemoveContactService(config.unit_of_work_factory, config.authorizer, scope),
        )
        self._customers = CustomerUseCases(
            create=CreateCustomerService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                names,
                CustomerFactory(),
                config.identifiers,
                config.clock,
                mapper,
                config.creation_fingerprinter,
            ),
            get=GetCustomerService(config.unit_of_work_factory, config.authorizer, scope, mapper),
            update=UpdateCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, names, config.clock, mapper
            ),
            archive=ArchiveCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, config.clock, mapper
            ),
            reactivate=ReactivateCustomerService(
                config.unit_of_work_factory, config.authorizer, scope, config.clock, mapper
            ),
            search=SearchCustomersService(
                config.unit_of_work_factory,
                config.authorizer,
                scope,
                CustomerSearchValidator(),
                mapper,
            ),
        )

    @property
    def customers(self) -> CustomerUseCases:
        return self._customers

    @property
    def contacts(self) -> ContactUseCases:
        return self._contacts

    @property
    def addresses(self) -> AddressUseCases:
        return self._addresses

    @property
    def preferences(self) -> PreferenceUseCases:
        return self._preferences

    @property
    def notes(self) -> NoteUseCases:
        return self._notes

    @property
    def config(self) -> CustomerModuleConfig:
        """Expose immutable host configuration until capability groups are implemented."""
        return self._config
