"""Shared Meta HTTP infrastructure."""

from .config import MetaApiConfig, MetaTimeoutConfig
from .contracts import MetaHttpObserver, MetaHttpTransport
from .decoder import MetaResponseDecoder
from .error_decoder import MetaErrorDecoder
from .errors import (
    MetaAuthenticationError,
    MetaInvalidResponseError,
    MetaProviderError,
    MetaRateLimitError,
    MetaTimeoutError,
    MetaTransientError,
)
from .executor import MetaRequestExecutor
from .models import MetaHttpMethod, MetaHttpRequest, MetaHttpResponse
from .observer import NullMetaHttpObserver
from .pagination import MetaPaginationCursorMapper
from .request_builder import MetaRequestBuilder
from .retry import MetaRetryPolicy
from .transport_httpx import HttpxMetaHttpTransport

__all__ = [
    "HttpxMetaHttpTransport",
    "MetaApiConfig",
    "MetaAuthenticationError",
    "MetaErrorDecoder",
    "MetaHttpMethod",
    "MetaHttpObserver",
    "MetaHttpRequest",
    "MetaHttpResponse",
    "MetaHttpTransport",
    "MetaInvalidResponseError",
    "MetaPaginationCursorMapper",
    "MetaProviderError",
    "MetaRateLimitError",
    "MetaRequestBuilder",
    "MetaRequestExecutor",
    "MetaResponseDecoder",
    "MetaRetryPolicy",
    "MetaTimeoutConfig",
    "MetaTimeoutError",
    "MetaTransientError",
    "NullMetaHttpObserver",
]
