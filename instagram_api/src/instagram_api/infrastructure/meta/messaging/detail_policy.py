"""Provider error policy for Instagram message-detail availability."""

from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramMessageDetailAvailabilityPolicy:
    """Recognizes provider failures caused by unavailable historical details."""

    def details_are_unavailable(self, error: MetaProviderError) -> bool:
        """Return whether message summary should be preserved without details."""

        return error.provider_code == 100
