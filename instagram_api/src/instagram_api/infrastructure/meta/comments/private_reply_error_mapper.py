"""Maps Meta private reply rejections to application-level errors."""

from instagram_api.application.comments.reply_errors import InstagramPrivateReplyIneligibleError
from instagram_api.infrastructure.meta.http import MetaProviderError


class MetaInstagramPrivateReplyErrorMapper:
    """Normalizes provider eligibility/window rejections."""

    def map(self, error: MetaProviderError) -> Exception:
        """Map provider request rejection while preserving infrastructure failures."""

        if error.status_code == 400:
            return InstagramPrivateReplyIneligibleError(error.message)

        return error
