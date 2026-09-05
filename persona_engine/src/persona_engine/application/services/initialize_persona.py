from persona_engine.application.contracts import PersonaGenerator
from persona_engine.application.models import PersonaInitializationInput
from persona_engine.application.policies import PersonaSourcePolicy
from persona_engine.domain import PersonaProfile


class InitializePersona:
    def __init__(
        self,
        *,
        source_policy: PersonaSourcePolicy,
        generator: PersonaGenerator,
    ) -> None:
        self._source_policy = source_policy
        self._generator = generator

    def execute(self, source: PersonaInitializationInput) -> PersonaProfile:
        texts = self._source_policy.validate(source)
        return self._generator.generate(PersonaInitializationInput(texts=texts))
