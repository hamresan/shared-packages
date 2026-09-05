from dataclasses import dataclass
from enum import StrEnum


class PersonaVerbosity(StrEnum):
    CONCISE = "concise"
    BALANCED = "balanced"
    DETAILED = "detailed"


class PersonaSentenceStyle(StrEnum):
    SHORT = "short"
    MIXED = "mixed"
    LONG = "long"


class PersonaUsageLevel(StrEnum):
    NONE = "none"
    LIGHT = "light"
    FREQUENT = "frequent"


class PersonaLineBreakStyle(StrEnum):
    COMPACT = "compact"
    SPACED = "spaced"


@dataclass(frozen=True, slots=True)
class PersonaProfile:
    source_sample_count: int
    verbosity: PersonaVerbosity
    sentence_style: PersonaSentenceStyle
    emoji_usage: PersonaUsageLevel
    hashtag_usage: PersonaUsageLevel
    exclamation_usage: PersonaUsageLevel
    line_break_style: PersonaLineBreakStyle
    guidelines: tuple[str, ...]
