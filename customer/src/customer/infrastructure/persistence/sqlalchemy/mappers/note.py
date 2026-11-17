from customer.domain.note import CustomerNote
from customer.infrastructure.persistence.sqlalchemy.models import CustomerNoteModel


class NoteMapper:
    @staticmethod
    def to_domain(row: CustomerNoteModel) -> CustomerNote:
        return CustomerNote(
            id=row.id,
            business_id=row.business_id,
            customer_id=row.customer_id,
            author_id=row.author_id,
            author_type=row.author_type,
            body=row.body,
            created_at=row.created_at,
        )

    @staticmethod
    def to_row(value: CustomerNote) -> CustomerNoteModel:
        return CustomerNoteModel(
            id=value.id,
            business_id=value.business_id,
            customer_id=value.customer_id,
            author_id=value.author_id,
            author_type=value.author_type,
            body=value.body,
            created_at=value.created_at,
        )
