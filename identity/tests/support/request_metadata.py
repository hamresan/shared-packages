from fastapi import Request

from identity.presentation.request_metadata import RequestMetadata, RequestMetadataResolver


class FixedRequestMetadataResolver(RequestMetadataResolver):
    def __init__(self, metadata: RequestMetadata) -> None:
        self._metadata = metadata

    def resolve(self, request: Request) -> RequestMetadata:
        return self._metadata
