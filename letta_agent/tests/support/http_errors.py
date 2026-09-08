import httpx
from letta_client import APIStatusError


def build_status_error(status_code: int) -> APIStatusError:
    request = httpx.Request("GET", "http://localhost/v1/test")
    response = httpx.Response(status_code, request=request)
    return APIStatusError(
        f"HTTP {status_code}",
        response=response,
        body=None,
    )


def build_not_found() -> APIStatusError:
    return build_status_error(404)
