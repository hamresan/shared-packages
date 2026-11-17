from customer.application.models.preference_result import PreferenceResult
from customer.domain.preference import CustomerPreference


class PreferenceResultMapper:
    def to_result(self, preference: CustomerPreference) -> PreferenceResult:
        return PreferenceResult(
            preference.id,
            preference.business_id,
            preference.customer_id,
            preference.key,
            preference.value,
        )
