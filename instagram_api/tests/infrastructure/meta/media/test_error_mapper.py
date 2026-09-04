"""Meta media error mapping tests."""

from instagram_api.application.media import InstagramMediaUnavailableError
from instagram_api.infrastructure.meta.http import MetaProviderError
from instagram_api.infrastructure.meta.media import MetaInstagramMediaErrorMapper


def test_error_mapper_maps_missing_media_failures() -> None:
    mapper = MetaInstagramMediaErrorMapper()

    by_status = mapper.map(MetaProviderError("missing", 404))
    by_code = mapper.map(MetaProviderError("missing", 400, provider_code=100))
    passthrough = MetaProviderError("other", 400)

    assert isinstance(by_status, InstagramMediaUnavailableError)
    assert isinstance(by_code, InstagramMediaUnavailableError)
    assert mapper.map(passthrough) is passthrough
