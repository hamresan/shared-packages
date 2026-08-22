# External protocol interoperability examples

These examples prove that Python and PHP can produce the same canonical request and HMAC-SHA256 signature byte-for-byte.

Run from `integration_auth/`:

```bash
python examples/interoperability/python_protocol.py
php examples/interoperability/php_protocol.php
python examples/interoperability/python_lifecycle_authorization.py
```

`vectors.json` contains deterministic **example-only** credentials. Never use these secrets in a real integration.

The examples intentionally use different inbound and outbound secrets. Credential direction is from the Python host perspective:

- `INBOUND`: external integration signs, Python verifies.
- `OUTBOUND`: Python signs, external integration verifies.

The Python lifecycle/authorization example also demonstrates:

- rotating only the inbound credential while leaving the outbound credential untouched;
- exact permission allow/deny behavior;
- exact resource-scope allow/deny behavior.

The examples use the same protocol rules as the package: RFC3986 query encoding, duplicate query preservation, SHA-256 body hashing, the canonical five-line request, lowercase hexadecimal HMAC-SHA256, and constant-time verification on the Python side.
