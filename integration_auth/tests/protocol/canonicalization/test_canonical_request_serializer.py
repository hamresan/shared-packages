from integration_auth.protocol.canonicalization.canonical_request_serializer import CanonicalRequestSerializer
from tests.support.protocol.canonical_request_builder import CanonicalRequestBuilder
from tests.support.protocol.known_answer_vector import EXPECTED_CANONICAL_REQUEST


def test_serializes_exact_known_answer_protocol_vector() -> None:
    assert CanonicalRequestSerializer().serialize(CanonicalRequestBuilder().build()) == (
        EXPECTED_CANONICAL_REQUEST
    )


def test_serializes_path_without_question_mark_when_query_is_empty() -> None:
    builder = CanonicalRequestBuilder()
    builder.path = "/health"
    builder.canonical_query = ""

    assert CanonicalRequestSerializer().serialize(builder.build()).splitlines()[1] == "/health"
