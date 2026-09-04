"""Meta comment reply response parsing tests."""

import pytest

from instagram_api.infrastructure.meta.comments import (
    MetaInstagramPrivateReplyResponseParser,
    MetaInstagramPublicReplyResponseParser,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


def test_reply_response_parsers_reject_missing_required_ids() -> None:
    with pytest.raises(MetaInvalidResponseError):
        MetaInstagramPublicReplyResponseParser().parse({})

    with pytest.raises(MetaInvalidResponseError):
        MetaInstagramPrivateReplyResponseParser().parse({"recipient_id": "recipient"})
