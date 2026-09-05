from persona_engine.application.models import PersonaInitializationInput


class PersonaSourcePolicy:
    def validate(self, source: PersonaInitializationInput) -> tuple[str, ...]:
        normalized = tuple(text.strip() for text in source.texts if text.strip())
        if not normalized:
            raise ValueError("Persona initialization requires account-authored text")
        return normalized
