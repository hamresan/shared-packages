"""Maps Meta media failures to application-level media errors."""

from instagram_api.application.media import InstagramMediaUnavailableError
from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramMediaErrorMapper:
    """Maps provider object-not-found failures to explicit media unavailability."""

    def raise_mapped(self, error: MetaProviderError) -> None:
        """Raise an application media error when the provider failure is recognized."""

        if error.status_code == 404 or error.provider_code == 100:
            raise InstagramMediaUnavailableError(
                "Requested Instagram media is deleted, inaccessible, or unavailable."
            ) from error

        raise error
