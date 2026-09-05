from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PersonaInitializationInput:
    texts: tuple[str, ...]
