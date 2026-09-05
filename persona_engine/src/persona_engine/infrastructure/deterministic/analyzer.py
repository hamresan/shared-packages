from collections.abc import Callable
from dataclasses import dataclass
import re
import unicodedata


@dataclass(frozen=True, slots=True)
class PersonaStyleMetrics:
    sample_count: int
    average_words: float
    average_sentence_words: float
    emoji_ratio: float
    hashtag_ratio: float
    exclamation_ratio: float
    multiline_ratio: float


class PersonaStyleAnalyzer:
    _sentence_pattern = re.compile(r"[.!?]+")

    def analyze(self, texts: tuple[str, ...]) -> PersonaStyleMetrics:
        word_counts = tuple(len(text.split()) for text in texts)
        sentence_word_counts = self._sentence_word_counts(texts)
        sample_count = len(texts)

        return PersonaStyleMetrics(
            sample_count=sample_count,
            average_words=sum(word_counts) / sample_count,
            average_sentence_words=(
                sum(sentence_word_counts) / len(sentence_word_counts)
                if sentence_word_counts
                else sum(word_counts) / sample_count
            ),
            emoji_ratio=self._ratio(texts, self._contains_emoji),
            hashtag_ratio=self._ratio(texts, lambda text: "#" in text),
            exclamation_ratio=self._ratio(texts, lambda text: "!" in text),
            multiline_ratio=self._ratio(texts, lambda text: "\n" in text),
        )

    def _sentence_word_counts(self, texts: tuple[str, ...]) -> tuple[int, ...]:
        counts: list[int] = []
        for text in texts:
            for sentence in self._sentence_pattern.split(text):
                word_count = len(sentence.split())
                if word_count:
                    counts.append(word_count)
        return tuple(counts)

    @staticmethod
    def _ratio(
        texts: tuple[str, ...],
        predicate: Callable[[str], bool],
    ) -> float:
        return sum(1 for text in texts if predicate(text)) / len(texts)

    @staticmethod
    def _contains_emoji(text: str) -> bool:
        return any(unicodedata.category(character) == "So" for character in text)
