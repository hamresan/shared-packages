from typing import cast

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from identity.presentation.request_metadata import (
    DirectRequestMetadataResolver,
    TrustedProxyRequestMetadataResolver,
)
from tests.support.http_client import JsonHttpClient


def test_direct_resolver_ignores_forwarded_for_header() -> None:
    app = FastAPI()
    resolver = DirectRequestMetadataResolver()

    async def resolve_metadata(request: Request) -> dict[str, str | None]:
        metadata = resolver.resolve(request)
        return {"ip": metadata.ip_address, "device": metadata.device_info}

    app.add_api_route("/", resolve_metadata, methods=["GET"])

    client = cast(JsonHttpClient, TestClient(app))
    response = client.get(
        "/",
        headers={
            "x-forwarded-for": "198.51.100.99",
            "user-agent": "metadata-test-agent",
        },
    )

    assert response.status_code == 200
    assert response.json()["ip"] != "198.51.100.99"
    assert response.json()["device"] == "metadata-test-agent"


def test_trusted_proxy_resolver_uses_configured_forwarded_hop() -> None:
    app = FastAPI()
    resolver = TrustedProxyRequestMetadataResolver(trusted_proxy_hops=2)

    async def resolve_metadata(request: Request) -> dict[str, str | None]:
        metadata = resolver.resolve(request)
        return {"ip": metadata.ip_address, "device": metadata.device_info}

    app.add_api_route("/", resolve_metadata, methods=["GET"])

    client = cast(JsonHttpClient, TestClient(app))
    response = client.get(
        "/",
        headers={
            "x-forwarded-for": "203.0.113.7, 10.0.0.10",
            "user-agent": "metadata-test-agent",
        },
    )

    assert response.status_code == 200
    assert response.json()["ip"] == "203.0.113.7"
    assert response.json()["device"] == "metadata-test-agent"
