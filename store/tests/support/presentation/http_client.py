from typing import Protocol, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response


class StoreHttpTestClient(Protocol):
    def get(self, url: str) -> Response: ...

    def post(self, url: str, *, json: object) -> Response: ...


def build_store_http_test_client(app: FastAPI) -> StoreHttpTestClient:
    return cast(StoreHttpTestClient, TestClient(app))
