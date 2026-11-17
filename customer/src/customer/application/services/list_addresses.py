from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.mapping.address_result import AddressResultMapper
from customer.application.models.address_result import AddressResult
from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy


class ListAddressesService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        mapper: AddressResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.mapper = mapper

    async def execute(self, query: CustomerDetailsQuery) -> tuple[AddressResult, ...]:
        async with self.uow(query.business_id) as transaction:
            await self.access.require(
                transaction.customers,
                query.business_id,
                query.customer_id,
                query.actor,
                CustomerPermission.READ,
                mutating=False,
            )
            addresses = await transaction.addresses.list_for_customer(
                query.business_id, query.customer_id
            )
            return tuple(self.mapper.to_result(address) for address in addresses)
