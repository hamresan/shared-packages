from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.mapping.address_result import AddressResultMapper
from customer.application.models.address_commands import UpdateAddressCommand
from customer.application.models.address_result import AddressResult
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.validation.address import AddressValidator
from customer.domain.errors import CustomerNotFoundError


class UpdateAddressService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        validator: AddressValidator,
        mapper: AddressResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.validator = validator
        self.mapper = mapper

    async def execute(self, command: UpdateAddressCommand) -> AddressResult:
        fields = self.validator.normalize(
            command.label,
            command.country_code,
            command.line1,
            command.city,
            command.region,
            command.postal_code,
        )
        async with self.uow() as transaction:
            await self.access.require(
                transaction.customers,
                command.business_id,
                command.customer_id,
                command.actor,
                CustomerPermission.UPDATE,
                mutating=True,
            )
            address = await transaction.addresses.get(
                command.business_id, command.customer_id, command.child_id
            )
            if address is None:
                raise CustomerNotFoundError("Address was not found")
            (
                address.label,
                address.country_code,
                address.line1,
                address.city,
                address.region,
                address.postal_code,
            ) = fields
            await transaction.addresses.save(address)
            await transaction.commit()
            return self.mapper.to_result(address)
