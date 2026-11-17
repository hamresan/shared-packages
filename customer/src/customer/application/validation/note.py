from customer.domain.errors import CustomerValidationError


class NoteValidator:
    def normalize(self, body: str) -> str:
        normalized = body.strip()
        if not (1 <= len(normalized) <= 4000):
            raise CustomerValidationError("Internal note must contain 1-4000 characters")
        return normalized
