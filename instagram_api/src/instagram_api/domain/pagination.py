"""Provider-neutral pagination models."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from .identifiers import PaginationCursor

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    """A normalized page of provider data."""

    items: tuple[T, ...]
    next_cursor: PaginationCursor | None = None
