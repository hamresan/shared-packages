"""Meta pagination cursor mapping tests."""

from instagram_api.domain import PaginationCursor
from instagram_api.infrastructure.meta.http import MetaPaginationCursorMapper


def test_pagination_mapper_extracts_after_cursor() -> None:
    mapper = MetaPaginationCursorMapper()

    cursor = mapper.next_cursor(
        {
            "paging": {
                "cursors": {
                    "before": "before",
                    "after": "after",
                }
            }
        }
    )

    assert cursor == PaginationCursor("after")


def test_pagination_mapper_returns_none_for_missing_or_invalid_cursor() -> None:
    mapper = MetaPaginationCursorMapper()

    assert mapper.next_cursor({}) is None
    assert mapper.next_cursor({"paging": {}}) is None
    assert mapper.next_cursor({"paging": {"cursors": {"after": ""}}}) is None
