"""Maps Meta public reply rejections to application-level errors."""

from instagram_api.application.comments.reply_errors import InstagramPublicReplyRejectedError
from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramPublicReplyErrorMapper:
    """Normalizes public comment reply rejections."""

    def map(self, error: MetaProviderError) -> Exception:
        """Map provider request rejection while preserving infrastructure failures."""

        if error.status_code == 400:
            return InstagramPublicReplyRejectedError(error.message)

        return error
