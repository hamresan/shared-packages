from customer.domain.errors import CustomerValidationError


class CustomerNameValidator:
    def normalize(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        if len(normalized) > 200:
            raise CustomerValidationError("Customer display name is too long")
        return normalized or None
