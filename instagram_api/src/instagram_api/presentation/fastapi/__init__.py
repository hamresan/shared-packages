"""Optional FastAPI infrastructure adapters."""

from .webhooks import create_instagram_webhook_router

__all__ = ["create_instagram_webhook_router"]
