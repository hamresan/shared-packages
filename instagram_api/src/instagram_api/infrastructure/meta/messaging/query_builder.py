"""Query builders for Meta Instagram messaging reads."""

from instagram_api.domain import PaginationCursor


class MetaInstagramMessageQueryBuilder:
    """Builds the Graph field expansion used to page conversation messages."""

    def fields(self, cursor: PaginationCursor | None) -> str:
        """Return the messages field expression for the requested page."""

        if cursor is None:
            return "messages"
        return f"messages.after({cursor})"
