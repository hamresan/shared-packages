from dataclasses import dataclass

from customer.application.models.profile_detail_commands import CustomerDetailsQuery


@dataclass(frozen=True, slots=True)
class AddNoteCommand(CustomerDetailsQuery):
    body: str
