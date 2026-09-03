"""Optional FastAPI transport adapter."""

from .config import InstagramFastApiConfig
from .contracts import InstagramFastApiCallbackResponder, InstagramFastApiOwnerContext
from .dependencies import InstagramFastApiDependencies
from .errors import InstagramFastApiErrorMapper
from .mappers import InstagramConnectionResponseMapper
from .router import create_instagram_auth_router
from .schemas import InstagramAuthorizationStartResponse, InstagramConnectionResponse

__all__ = [
    "InstagramAuthorizationStartResponse",
    "InstagramConnectionResponse",
    "InstagramConnectionResponseMapper",
    "InstagramFastApiCallbackResponder",
    "InstagramFastApiConfig",
    "InstagramFastApiDependencies",
    "InstagramFastApiErrorMapper",
    "InstagramFastApiOwnerContext",
    "create_instagram_auth_router",
]
