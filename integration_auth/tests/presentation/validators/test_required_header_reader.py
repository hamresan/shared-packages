"""Tests for required integration authentication header validation."""

import pytest

from integration_auth.presentation.validators.required_header_reader import (
    InvalidSignedRequestHeadersError,
    RequiredHeaderReader,
)
from tests.support.presentation.request_builder import FastApiRequestBuilder


def test_required_header_reader_returns_trimmed_value() -> None:
    request = FastApiRequestBuilder().build(headers={"X-Test": "  value  "})

    assert RequiredHeaderReader().read(request, "X-Test") == "value"


def test_required_header_reader_rejects_missing_header() -> None:
    request = FastApiRequestBuilder().build()

    with pytest.raises(InvalidSignedRequestHeadersError):
        RequiredHeaderReader().read(request, "X-Test")


def test_required_header_reader_rejects_blank_header() -> None:
    request = FastApiRequestBuilder().build(headers={"X-Test": "   "})

    with pytest.raises(InvalidSignedRequestHeadersError):
        RequiredHeaderReader().read(request, "X-Test")
