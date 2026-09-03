"""Provider-independent Instagram authorization errors."""

from dataclasses import dataclass

from instagram_auth.baseline import InstagramProviderErrorKind


@dataclass(frozen=True, slots=True)
class InstagramProviderError(Exception):
    """Safe normalized provider failure exposed to application consumers."""

    kind: InstagramProviderErrorKind
    message: str
    status_code: int | None = None

    def __str__(self) -> str:
        return self.message
