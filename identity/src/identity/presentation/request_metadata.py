from dataclasses import dataclass
from typing import Protocol

from fastapi import Request


@dataclass(frozen=True, slots=True)
class RequestMetadata:
    ip_address: str | None
    device_info: str | None


class RequestMetadataResolver(Protocol):
    def resolve(self, request: Request) -> RequestMetadata: ...


class DirectRequestMetadataResolver(RequestMetadataResolver):
    def resolve(self, request: Request) -> RequestMetadata:
        return RequestMetadata(
            ip_address=request.client.host if request.client is not None else None,
            device_info=request.headers.get("user-agent"),
        )


class TrustedProxyRequestMetadataResolver(RequestMetadataResolver):
    def __init__(self, trusted_proxy_hops: int = 1) -> None:
        if trusted_proxy_hops < 1:
            raise ValueError("trusted_proxy_hops must be at least 1")
        self._trusted_proxy_hops = trusted_proxy_hops

    def resolve(self, request: Request) -> RequestMetadata:
        forwarded_for = request.headers.get("x-forwarded-for")
        ip_address = self._resolve_forwarded_ip(forwarded_for)
        if ip_address is None and request.client is not None:
            ip_address = request.client.host
        return RequestMetadata(
            ip_address=ip_address,
            device_info=request.headers.get("user-agent"),
        )

    def _resolve_forwarded_ip(self, forwarded_for: str | None) -> str | None:
        if not forwarded_for:
            return None
        addresses = [part.strip() for part in forwarded_for.split(",") if part.strip()]
        if len(addresses) < self._trusted_proxy_hops:
            return None
        return addresses[-self._trusted_proxy_hops]


__all__ = [
    "DirectRequestMetadataResolver",
    "RequestMetadata",
    "RequestMetadataResolver",
    "TrustedProxyRequestMetadataResolver",
]
