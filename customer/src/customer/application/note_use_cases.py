from dataclasses import dataclass

from customer.application.services.add_note import AddNoteService
from customer.application.services.list_notes import ListNotesService
from customer.application.services.remove_note import RemoveNoteService


@dataclass(frozen=True, slots=True)
class NoteUseCases:
    add: AddNoteService
    list: ListNotesService
    remove: RemoveNoteService
