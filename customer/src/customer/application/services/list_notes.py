from customer.application.contracts import CustomerUnitOfWorkFactory
from customer.application.mapping.note_result import NoteResultMapper
from customer.application.models.note_result import NoteResult
from customer.application.models.profile_detail_commands import CustomerDetailsQuery
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy


class ListNotesService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        mapper: NoteResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.mapper = mapper

    async def execute(self, query: CustomerDetailsQuery) -> tuple[NoteResult, ...]:
        async with self.uow(query.business_id) as transaction:
            await self.access.require(
                transaction.customers,
                query.business_id,
                query.customer_id,
                query.actor,
                CustomerPermission.NOTES_READ,
                mutating=False,
            )
            notes = await transaction.notes.list_for_customer(query.business_id, query.customer_id)
            return tuple(self.mapper.to_result(note) for note in notes)
