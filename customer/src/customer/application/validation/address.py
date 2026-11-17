from customer.domain.errors import CustomerValidationError


class AddressValidator:
    def normalize(
        self,
        label: str,
        country_code: str,
        line1: str,
        city: str,
        region: str | None,
        postal_code: str | None,
    ) -> tuple[str, str, str, str, str | None, str | None]:
        normalized_label = label.strip()
        normalized_country = country_code.strip().upper()
        normalized_line = line1.strip()
        normalized_city = city.strip()
        normalized_region = region.strip() if region is not None else None
        normalized_postal = postal_code.strip() if postal_code is not None else None
        if not (1 <= len(normalized_label) <= 80):
            raise CustomerValidationError("Invalid address label")
        if len(normalized_country) != 2 or not normalized_country.isalpha():
            raise CustomerValidationError("Country code must have two letters")
        if not (1 <= len(normalized_line) <= 300) or not (1 <= len(normalized_city) <= 150):
            raise CustomerValidationError("Invalid address line or city")
        if (normalized_region is not None and len(normalized_region) > 150) or (
            normalized_postal is not None and len(normalized_postal) > 40
        ):
            raise CustomerValidationError("Address region or postal code is too long")
        return (
            normalized_label,
            normalized_country,
            normalized_line,
            normalized_city,
            normalized_region or None,
            normalized_postal or None,
        )
