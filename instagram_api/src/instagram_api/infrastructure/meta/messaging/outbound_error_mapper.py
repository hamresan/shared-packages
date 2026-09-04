"""Maps Meta Send API rejections to application-level errors."""

from instagram_api.application.messaging import InstagramMessageSendRejectedError
from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramMessageSendErrorMapper:
    """Normalizes provider policy/request rejections without guessing subtypes."""

    def map(self, error: MetaProviderError) -> Exception:
        """Map provider request rejection while preserving infrastructure failures."""

        if error.status_code == 400:
            return InstagramMessageSendRejectedError(error.message)

        return error
