from customer.application.contracts import CustomerUnitOfWorkFactory, IdentifierGenerator
from customer.application.mapping.address_result import AddressResultMapper
from customer.application.models.address_commands import AddAddressCommand
from customer.application.models.address_result import AddressResult
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.validation.address import AddressValidator
from customer.domain.address import CustomerAddress


class AddAddressService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        validator: AddressValidator,
        identifiers: IdentifierGenerator,
        mapper: AddressResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.validator = validator
        self.identifiers = identifiers
        self.mapper = mapper

    async def execute(self, command: AddAddressCommand) -> AddressResult:
        fields = self.validator.normalize(
            command.label,
            command.country_code,
            command.line1,
            command.city,
            command.region,
            command.postal_code,
        )
        async with self.uow(command.business_id) as transaction:
            await self.access.require(
                transaction.customers,
                command.business_id,
                command.customer_id,
                command.actor,
                CustomerPermission.UPDATE,
                mutating=True,
            )
            if command.is_default:
                await transaction.addresses.unset_default(command.business_id, command.customer_id)
            address = CustomerAddress(
                self.identifiers.new_id(),
                command.business_id,
                command.customer_id,
                *fields,
                command.is_default,
            )
            await transaction.addresses.add(address)
            await transaction.commit_audited(command.actor, "address.add", command.customer_id)
            return self.mapper.to_result(address)
