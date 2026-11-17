from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.mapping.address_result import AddressResultMapper
from customer.application.models.address_result import AddressResult
from customer.application.models.profile_detail_commands import CustomerChildMutation
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.domain.errors import CustomerNotFoundError


class SetDefaultAddressService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        mapper: AddressResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.mapper = mapper

    async def execute(self, command: CustomerChildMutation) -> AddressResult:
        async with self.uow(command.business_id) as transaction:
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
            await transaction.addresses.unset_default(command.business_id, command.customer_id)
            address.is_default = True
            await transaction.addresses.save(address)
            await transaction.commit_audited(
                command.actor, "address.set_default", command.customer_id
            )
            return self.mapper.to_result(address)
