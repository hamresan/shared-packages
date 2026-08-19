import pytest

from subscription import SubjectReference


def test_subject_reference_accepts_generic_subject_and_identifier() -> None:
    reference = SubjectReference(
        subject_type="store",
        subject_id="550e8400-e29b-41d4-a716-446655440000",
    )

    assert reference.subject_type == "store"
    assert reference.subject_id == "550e8400-e29b-41d4-a716-446655440000"


def test_subject_reference_does_not_require_uuid_identifier() -> None:
    reference = SubjectReference(subject_type="workspace", subject_id="workspace-42")

    assert reference.subject_id == "workspace-42"


@pytest.mark.parametrize(
    "subject_type",
    ["", "Store", "store type", "_store", "store/type", "a" * 65],
)
def test_subject_reference_rejects_non_canonical_subject_type(subject_type: str) -> None:
    with pytest.raises(ValueError, match="subject_type"):
        SubjectReference(subject_type=subject_type, subject_id="123")


@pytest.mark.parametrize("subject_id", ["", " 123", "123 ", " "])
def test_subject_reference_rejects_empty_or_untrimmed_identifier(subject_id: str) -> None:
    with pytest.raises(ValueError, match="subject_id"):
        SubjectReference(subject_type="user", subject_id=subject_id)


def test_subject_reference_rejects_identifier_longer_than_255_characters() -> None:
    with pytest.raises(ValueError, match="255"):
        SubjectReference(subject_type="organization", subject_id="x" * 256)
