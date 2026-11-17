from customer.application.models.customer_queries import CustomerSearchQuery
from customer.domain.errors import CustomerValidationError


class CustomerSearchValidator:
    def validate(self, query: CustomerSearchQuery) -> None:
        if query.offset < 0 or query.limit < 1 or query.limit > 100:
            raise CustomerValidationError("Invalid customer search pagination")
        if query.name_contains is not None and len(query.name_contains) > 200:
            raise CustomerValidationError("Customer search query is too long")
