from dataclasses import dataclass

from customer.application.services.list_preferences import ListPreferencesService
from customer.application.services.remove_preference import RemovePreferenceService
from customer.application.services.set_preference import SetPreferenceService


@dataclass(frozen=True, slots=True)
class PreferenceUseCases:
    set: SetPreferenceService
    list: ListPreferencesService
    remove: RemovePreferenceService
