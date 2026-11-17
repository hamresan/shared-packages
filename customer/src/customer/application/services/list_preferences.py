from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.mapping.preference_result import PreferenceResultMapper
from customer.application.models.preference_result import PreferenceResult
from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy


class ListPreferencesService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        mapper: PreferenceResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.mapper = mapper

    async def execute(self, query: CustomerDetailsQuery) -> tuple[PreferenceResult, ...]:
        async with self.uow() as transaction:
            await self.access.require(
                transaction.customers,
                query.business_id,
                query.customer_id,
                query.actor,
                CustomerPermission.READ,
                mutating=False,
            )
            preferences = await transaction.preferences.list_for_customer(
                query.business_id, query.customer_id
            )
            return tuple(self.mapper.to_result(preference) for preference in preferences)
