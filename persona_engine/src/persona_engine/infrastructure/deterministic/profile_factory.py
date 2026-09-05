from persona_engine.domain import (
    PersonaLineBreakStyle,
    PersonaProfile,
    PersonaSentenceStyle,
    PersonaUsageLevel,
    PersonaVerbosity,
)
from persona_engine.infrastructure.deterministic.analyzer import PersonaStyleMetrics


class DeterministicPersonaProfileFactory:
    def build(self, metrics: PersonaStyleMetrics) -> PersonaProfile:
        verbosity = self._verbosity(metrics.average_words)
        sentence_style = self._sentence_style(metrics.average_sentence_words)
        emoji_usage = self._usage(metrics.emoji_ratio)
        hashtag_usage = self._usage(metrics.hashtag_ratio)
        exclamation_usage = self._usage(metrics.exclamation_ratio)
        line_break_style = (
            PersonaLineBreakStyle.SPACED
            if metrics.multiline_ratio >= 0.35
            else PersonaLineBreakStyle.COMPACT
        )

        return PersonaProfile(
            source_sample_count=metrics.sample_count,
            verbosity=verbosity,
            sentence_style=sentence_style,
            emoji_usage=emoji_usage,
            hashtag_usage=hashtag_usage,
            exclamation_usage=exclamation_usage,
            line_break_style=line_break_style,
            guidelines=self._guidelines(
                verbosity=verbosity,
                sentence_style=sentence_style,
                emoji_usage=emoji_usage,
                hashtag_usage=hashtag_usage,
                exclamation_usage=exclamation_usage,
                line_break_style=line_break_style,
            ),
        )

    @staticmethod
    def _verbosity(average_words: float) -> PersonaVerbosity:
        if average_words <= 12:
            return PersonaVerbosity.CONCISE
        if average_words >= 35:
            return PersonaVerbosity.DETAILED
        return PersonaVerbosity.BALANCED

    @staticmethod
    def _sentence_style(average_sentence_words: float) -> PersonaSentenceStyle:
        if average_sentence_words <= 8:
            return PersonaSentenceStyle.SHORT
        if average_sentence_words >= 20:
            return PersonaSentenceStyle.LONG
        return PersonaSentenceStyle.MIXED

    @staticmethod
    def _usage(ratio: float) -> PersonaUsageLevel:
        if ratio == 0:
            return PersonaUsageLevel.NONE
        if ratio >= 0.5:
            return PersonaUsageLevel.FREQUENT
        return PersonaUsageLevel.LIGHT

    @staticmethod
    def _guidelines(
        *,
        verbosity: PersonaVerbosity,
        sentence_style: PersonaSentenceStyle,
        emoji_usage: PersonaUsageLevel,
        hashtag_usage: PersonaUsageLevel,
        exclamation_usage: PersonaUsageLevel,
        line_break_style: PersonaLineBreakStyle,
    ) -> tuple[str, ...]:
        return (
            f"Keep responses {verbosity.value}.",
            f"Prefer {sentence_style.value} sentence structure.",
            f"Use emojis at a {emoji_usage.value} level.",
            f"Use hashtags at a {hashtag_usage.value} level.",
            f"Use exclamation marks at a {exclamation_usage.value} level.",
            f"Keep paragraph layout {line_break_style.value}.",
        )
