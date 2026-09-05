import pytest

from persona_engine import (
    DeterministicPersonaGenerator,
    DeterministicPersonaProfileFactory,
    InitializePersona,
    PersonaInitializationInput,
    PersonaSourcePolicy,
    PersonaStyleAnalyzer,
)


def build_service() -> InitializePersona:
    return InitializePersona(
        source_policy=PersonaSourcePolicy(),
        generator=DeterministicPersonaGenerator(
            analyzer=PersonaStyleAnalyzer(),
            profile_factory=DeterministicPersonaProfileFactory(),
        ),
    )


def test_initialize_persona_normalizes_and_generates_profile() -> None:
    result = build_service().execute(
        PersonaInitializationInput(
            texts=(
                "  Short caption! 😊  ",
                "",
                "Another short caption #shop",
            )
        )
    )

    assert result.source_sample_count == 2
    assert result.guidelines


def test_initialize_persona_rejects_empty_source() -> None:
    with pytest.raises(ValueError, match="requires account-authored text"):
        build_service().execute(PersonaInitializationInput(texts=("", "   ")))
