# Identity Rate Limiting

Identity applies application-level OTP abuse controls by default.

## Default limits

- OTP requests per normalized destination: 5 per 15 minutes.
- OTP requests per normalized destination: 20 per 24 hours.
- OTP verification attempts per challenge: 10 per minute.

These controls are independent of the OTP resend cooldown and the maximum invalid OTP attempt count.

## Deployment model

The default `InMemoryRateLimiter` is process-local. It provides a secure baseline for a single application process and for development, but it does not coordinate counters across multiple workers or hosts.

Production deployments with multiple processes or instances should inject a distributed implementation of the public `RateLimiter` contract through `IdentityModuleConfig.rate_limiter`. Redis or another atomic shared counter store is an appropriate implementation choice at the host boundary.

Coarse traffic throttling should also remain enabled at nginx, an API gateway, or a WAF. Application-level limits are intended to enforce identity-specific semantics and are not a replacement for edge throttling.

## Client IP

The current security policy does not use `ip_address` from OTP/session request bodies for rate-limit decisions because that value is client supplied and therefore untrusted. Per-IP limits should be added after the presentation layer resolves client IP from trusted proxy-aware request metadata.
