"""Maps Meta media failures to application-level media errors."""

from instagram_api.application.media import InstagramMediaUnavailableError
from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramMediaErrorMapper:
    """Maps provider failures to media-specific application errors."""

    def map(self, error: MetaProviderError) -> Exception:
        """Return the appropriate media-level or provider exception."""

        if error.status_code == 404 or error.provider_code == 100:
            return InstagramMediaUnavailableError(
                "Requested Instagram media is deleted, inaccessible, or unavailable."
            )

        return error
