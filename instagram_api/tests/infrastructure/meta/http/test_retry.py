"""Safe Meta retry policy tests."""

from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaRateLimitError,
    MetaRetryPolicy,
    MetaTransientError,
)


def test_retry_policy_retries_only_idempotent_get_failures() -> None:
    policy = MetaRetryPolicy(max_attempts=3)

    assert policy.should_retry(
        method=MetaHttpMethod.GET,
        error=MetaTransientError("temporary", 500),
        attempt=1,
    )
    assert policy.should_retry(
        method=MetaHttpMethod.GET,
        error=MetaRateLimitError("limited", 429),
        attempt=2,
    )
    assert not policy.should_retry(
        method=MetaHttpMethod.POST,
        error=MetaTransientError("temporary", 500),
        attempt=1,
    )
    assert not policy.should_retry(
        method=MetaHttpMethod.GET,
        error=MetaTransientError("temporary", 500),
        attempt=3,
    )


def test_retry_policy_delay_is_bounded() -> None:
    policy = MetaRetryPolicy(
        base_delay_seconds=0.5,
        max_delay_seconds=1.0,
    )

    assert policy.delay_seconds(1) == 0.5
    assert policy.delay_seconds(2) == 1.0
    assert policy.delay_seconds(10) == 1.0
