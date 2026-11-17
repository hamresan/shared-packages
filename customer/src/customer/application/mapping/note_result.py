from customer.application.models.note_result import NoteResult
from customer.domain.note import CustomerNote


class NoteResultMapper:
    def to_result(self, note: CustomerNote) -> NoteResult:
        return NoteResult(
            note.id,
            note.business_id,
            note.customer_id,
            note.author_id,
            note.author_type,
            note.body,
            note.created_at,
        )
