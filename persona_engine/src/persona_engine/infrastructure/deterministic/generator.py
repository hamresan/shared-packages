from persona_engine.application.contracts import PersonaGenerator
from persona_engine.application.models import PersonaInitializationInput
from persona_engine.domain import PersonaProfile
from persona_engine.infrastructure.deterministic.analyzer import PersonaStyleAnalyzer
from persona_engine.infrastructure.deterministic.profile_factory import (
    DeterministicPersonaProfileFactory,
)


class DeterministicPersonaGenerator(PersonaGenerator):
    def __init__(
        self,
        *,
        analyzer: PersonaStyleAnalyzer,
        profile_factory: DeterministicPersonaProfileFactory,
    ) -> None:
        self._analyzer = analyzer
        self._profile_factory = profile_factory

    def generate(self, source: PersonaInitializationInput) -> PersonaProfile:
        metrics = self._analyzer.analyze(source.texts)
        return self._profile_factory.build(metrics)
