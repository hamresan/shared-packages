import re
from dataclasses import dataclass

_SUBJECT_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9._-]{0,63}$")
_MAX_SUBJECT_ID_LENGTH = 255


@dataclass(frozen=True, slots=True)
class SubjectReference:
    """Generic reference to a subscription owner in a consuming application."""

    subject_type: str
    subject_id: str

    def __post_init__(self) -> None:
        if not _SUBJECT_TYPE_PATTERN.fullmatch(self.subject_type):
            raise ValueError(
                "subject_type must be a canonical lowercase identifier containing only "
                "letters, digits, '.', '_' or '-'"
            )
        if not self.subject_id or self.subject_id != self.subject_id.strip():
            raise ValueError("subject_id must be a non-empty trimmed string")
        if len(self.subject_id) > _MAX_SUBJECT_ID_LENGTH:
            raise ValueError(f"subject_id must not exceed {_MAX_SUBJECT_ID_LENGTH} characters")
