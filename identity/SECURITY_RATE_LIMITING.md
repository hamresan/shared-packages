# Identity Rate Limiting

This file is retained as a security-oriented summary. `RATE_LIMITING.md` is the detailed source of truth for current behavior and deployment requirements.

Identity applies application-level OTP abuse controls by default.

## Default limits

- OTP requests per normalized destination: 5 per 15 minutes.
- OTP requests per normalized destination: 20 per 24 hours.
- OTP requests per trusted requester/IP: 30 per 15 minutes.
- OTP verification attempts per challenge: 10 per minute.

These controls are independent of the OTP resend cooldown and the maximum invalid OTP attempt count.

## Deployment model

The default `InMemoryRateLimiter` is process-local. It is suitable for tests, development, and deliberately single-process deployments, but it does not coordinate counters across multiple workers or hosts.

Production deployments with multiple processes or instances must inject a distributed implementation of the public `RateLimiter` contract through `IdentityModuleConfig.rate_limiter`. Redis or another atomic shared counter store is an appropriate implementation choice at the host boundary.

Do not silently fall back to process-local counters in a multi-instance production topology if the distributed backend becomes unavailable; that would weaken rate-limit enforcement differently on each instance.

Coarse traffic throttling should also remain enabled at nginx, an API gateway, or a WAF. Application-level limits enforce Identity-specific destination/requester/challenge semantics and are not a replacement for edge throttling.

## Trusted requester/IP limits

Identity does not trust `ip_address` fields supplied in request bodies.

FastAPI resolves requester metadata server-side through `RequestMetadataResolver`:

- `DirectRequestMetadataResolver` uses the direct socket peer and ignores `X-Forwarded-For`;
- `TrustedProxyRequestMetadataResolver` may use a configured trusted forwarded hop only when the host explicitly enables it for a controlled proxy topology;
- requester IP values are validated and canonicalized before they become rate-limit keys, so equivalent IPv4/IPv6 textual representations share the same requester bucket.

The requester bucket is shared across destinations, preventing one source from bypassing destination limits by cycling through many email addresses or phone numbers.

See `RATE_LIMITING.md`, `TRUSTED_REQUEST_METADATA.md`, and `DEPLOYMENT_SECURITY.md` before configuring production proxy trust or distributed rate limiting.
