from typing import Protocol

from persona_engine.application.models import PersonaInitializationInput
from persona_engine.domain import PersonaProfile


class PersonaGenerator(Protocol):
    def generate(self, source: PersonaInitializationInput) -> PersonaProfile: ...
