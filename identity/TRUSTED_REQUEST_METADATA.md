# Trusted request metadata

Identity session metadata must not be accepted from request bodies.

The FastAPI adapter resolves `ip_address` and `device_info` from the HTTP request before creating application commands:

- `device_info` comes from the observed `User-Agent` header.
- `ip_address` comes from the socket peer by default.
- `X-Forwarded-For` is ignored by default.

## Default deployment

`DirectRequestMetadataResolver` is the safe default. It uses `request.client.host` and never trusts forwarding headers.

## Trusted reverse proxy deployment

When the application is reachable only through a controlled reverse proxy such as nginx, the host may explicitly configure `TrustedProxyRequestMetadataResolver` and set the expected number of trusted proxy hops.

The application must not be directly reachable from untrusted networks when forwarding headers are trusted. The proxy must overwrite or correctly append forwarding headers.

Example composition:

```python
IdentityModuleConfig(
    ...,
    request_metadata_resolver=TrustedProxyRequestMetadataResolver(
        trusted_proxy_hops=1,
    ),
)
```

For multiple trusted proxy hops, configure the exact hop count for the deployment topology.

Do not use client-provided JSON fields for IP address, device information, security logging, or future per-IP rate limiting decisions.
