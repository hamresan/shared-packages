from dataclasses import dataclass
from typing import Protocol

from fastapi import Request

from identity.presentation.ip_address import IpAddressNormalizer


@dataclass(frozen=True, slots=True)
class RequestMetadata:
    ip_address: str | None
    device_info: str | None


class RequestMetadataResolver(Protocol):
    def resolve(self, request: Request) -> RequestMetadata: ...


class ForwardedForParser:
    def __init__(self, ip_normalizer: IpAddressNormalizer | None = None) -> None:
        self._ip_normalizer = ip_normalizer or IpAddressNormalizer()

    def parse(self, value: str | None, trusted_proxy_hops: int) -> str | None:
        if not value:
            return None
        addresses = [part.strip() for part in value.split(",") if part.strip()]
        if len(addresses) < trusted_proxy_hops:
            return None
        return self._ip_normalizer.normalize(addresses[-trusted_proxy_hops])


class DirectRequestMetadataResolver(RequestMetadataResolver):
    def __init__(self, ip_normalizer: IpAddressNormalizer | None = None) -> None:
        self._ip_normalizer = ip_normalizer or IpAddressNormalizer()

    def resolve(self, request: Request) -> RequestMetadata:
        peer_address = request.client.host if request.client is not None else None
        return RequestMetadata(
            ip_address=self._ip_normalizer.normalize(peer_address),
            device_info=request.headers.get("user-agent"),
        )


class TrustedProxyRequestMetadataResolver(RequestMetadataResolver):
    def __init__(
        self,
        trusted_proxy_hops: int = 1,
        forwarded_for_parser: ForwardedForParser | None = None,
        ip_normalizer: IpAddressNormalizer | None = None,
    ) -> None:
        if trusted_proxy_hops < 1:
            raise ValueError("trusted_proxy_hops must be at least 1")
        self._trusted_proxy_hops = trusted_proxy_hops
        self._ip_normalizer = ip_normalizer or IpAddressNormalizer()
        self._forwarded_for_parser = forwarded_for_parser or ForwardedForParser(self._ip_normalizer)

    def resolve(self, request: Request) -> RequestMetadata:
        ip_address = self._forwarded_for_parser.parse(
            request.headers.get("x-forwarded-for"),
            self._trusted_proxy_hops,
        )
        if ip_address is None and request.client is not None:
            ip_address = self._ip_normalizer.normalize(request.client.host)
        return RequestMetadata(
            ip_address=ip_address,
            device_info=request.headers.get("user-agent"),
        )


__all__ = [
    "DirectRequestMetadataResolver",
    "ForwardedForParser",
    "RequestMetadata",
    "RequestMetadataResolver",
    "TrustedProxyRequestMetadataResolver",
]
