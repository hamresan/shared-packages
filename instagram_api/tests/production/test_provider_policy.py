"""Production policy checks for versioning and safe retries."""

from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaHttpMethod,
    MetaRateLimitError,
    MetaRetryPolicy,
)


def test_meta_api_config_always_builds_a_versioned_url() -> None:
    config = MetaApiConfig(api_version="v99.0")

    assert config.build_url("me") == "https://graph.instagram.com/v99.0/me"


def test_rate_limit_retry_is_bounded_and_get_only() -> None:
    policy = MetaRetryPolicy(max_attempts=3)
    error = MetaRateLimitError(
        message="rate limited",
        status_code=429,
    )

    assert policy.should_retry(method=MetaHttpMethod.GET, error=error, attempt=1)
    assert not policy.should_retry(method=MetaHttpMethod.POST, error=error, attempt=1)
    assert not policy.should_retry(method=MetaHttpMethod.GET, error=error, attempt=3)
    assert policy.delay_seconds(10) <= policy.max_delay_seconds
