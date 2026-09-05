from persona_engine import (
    DeterministicPersonaGenerator,
    DeterministicPersonaProfileFactory,
    PersonaInitializationInput,
    PersonaLineBreakStyle,
    PersonaSentenceStyle,
    PersonaStyleAnalyzer,
    PersonaUsageLevel,
    PersonaVerbosity,
)


def build_generator() -> DeterministicPersonaGenerator:
    return DeterministicPersonaGenerator(
        analyzer=PersonaStyleAnalyzer(),
        profile_factory=DeterministicPersonaProfileFactory(),
    )


def test_generator_extracts_observable_style_without_business_facts() -> None:
    result = build_generator().generate(
        PersonaInitializationInput(
            texts=(
                "Fresh arrivals! 😊\nTap to explore #new",
                "Weekend picks! ✨\nShop now #style",
            )
        )
    )

    assert result.verbosity is PersonaVerbosity.CONCISE
    assert result.sentence_style is PersonaSentenceStyle.SHORT
    assert result.emoji_usage is PersonaUsageLevel.FREQUENT
    assert result.hashtag_usage is PersonaUsageLevel.FREQUENT
    assert result.exclamation_usage is PersonaUsageLevel.FREQUENT
    assert result.line_break_style is PersonaLineBreakStyle.SPACED
    assert all("Fresh arrivals" not in guideline for guideline in result.guidelines)


def test_generator_classifies_long_plain_text_style() -> None:
    long_sentence = " ".join(["word"] * 40)

    result = build_generator().generate(
        PersonaInitializationInput(texts=(long_sentence,))
    )

    assert result.verbosity is PersonaVerbosity.DETAILED
    assert result.sentence_style is PersonaSentenceStyle.LONG
    assert result.emoji_usage is PersonaUsageLevel.NONE
    assert result.hashtag_usage is PersonaUsageLevel.NONE
    assert result.exclamation_usage is PersonaUsageLevel.NONE
    assert result.line_break_style is PersonaLineBreakStyle.COMPACT
