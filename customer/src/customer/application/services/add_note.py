from customer.application.contracts import Clock, CustomerUnitOfWorkFactory, IdentifierGenerator
from customer.application.mapping.note_result import NoteResultMapper
from customer.application.models.note_commands import AddNoteCommand
from customer.application.models.note_result import NoteResult
from customer.application.permissions import CustomerPermission
from customer.application.policies.detail_access import CustomerDetailAccessPolicy
from customer.application.validation.note import NoteValidator
from customer.domain.note import CustomerNote


class AddNoteService:
    def __init__(
        self,
        uow: CustomerUnitOfWorkFactory,
        access: CustomerDetailAccessPolicy,
        validator: NoteValidator,
        identifiers: IdentifierGenerator,
        clock: Clock,
        mapper: NoteResultMapper,
    ) -> None:
        self.uow = uow
        self.access = access
        self.validator = validator
        self.identifiers = identifiers
        self.clock = clock
        self.mapper = mapper

    async def execute(self, command: AddNoteCommand) -> NoteResult:
        body = self.validator.normalize(command.body)
        async with self.uow(command.business_id) as transaction:
            await self.access.require(
                transaction.customers,
                command.business_id,
                command.customer_id,
                command.actor,
                CustomerPermission.NOTES_WRITE,
                mutating=True,
            )
            note = CustomerNote(
                self.identifiers.new_id(),
                command.business_id,
                command.customer_id,
                command.actor.actor_id,
                command.actor.actor_type.value,
                body,
                self.clock.now(),
            )
            await transaction.notes.add(note)
            await transaction.commit_audited(command.actor, "note.add", command.customer_id)
            return self.mapper.to_result(note)
