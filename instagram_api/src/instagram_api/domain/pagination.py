"""Provider-neutral pagination models."""

from dataclasses import dataclass

from .identifiers import PaginationCursor


@dataclass(frozen=True, slots=True)
class Page[T]:
    """A normalized page of provider data."""

    items: tuple[T, ...]
    next_cursor: PaginationCursor | None = None
