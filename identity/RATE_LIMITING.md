# Identity rate limiting

Identity applies application-level OTP rate limits through the `RateLimiter` contract. The default in-memory implementation is suitable for tests and single-process development. Production deployments with more than one application instance should inject a distributed implementation such as Redis-backed rate limiting.

## OTP request scopes

OTP requests are limited independently by:

- canonical destination burst limit;
- canonical destination daily limit;
- trusted requester/IP burst limit when request metadata contains an IP address.

The requester scope is shared across destinations. This prevents one client from bypassing destination-specific limits by requesting OTPs for many different phone numbers or email addresses.

Default requester settings are 30 OTP requests per 15 minutes and can be changed through `IdentityModuleConfig.otp_requester_burst_limit` and `IdentityModuleConfig.otp_requester_burst_window`.

## Trusted requester metadata

The package does not trust client-supplied IP fields. FastAPI resolves request metadata server-side through `RequestMetadataResolver`.

`DirectRequestMetadataResolver` is the safe default and uses the direct socket peer (`request.client.host`). It ignores `X-Forwarded-For`.

When Identity is deployed behind a trusted reverse proxy, the host may configure `TrustedProxyRequestMetadataResolver` with the known proxy hop count. Only do this when nginx or the upstream gateway removes/replaces untrusted forwarding headers and the application is not directly reachable around that proxy.

Do not enable forwarded-header trust merely because an `X-Forwarded-For` header is present. A client-controlled forwarding header would allow requester-rate-limit bypass.

## Edge throttling

Application rate limiting is not a replacement for coarse traffic controls at nginx, an API gateway, or a WAF. Production deployments should use both layers: edge throttling for volumetric abuse and Identity's semantic limits for destination/requester/challenge abuse.
