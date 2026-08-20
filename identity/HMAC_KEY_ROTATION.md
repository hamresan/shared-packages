# HMAC key rotation

Identity stores OTP codes and refresh tokens as HMAC-SHA256 hashes. New hashes are versioned with the key identifier used to create them:

```text
hmac-sha256$<key-id>$<digest>
```

`IdentityModuleConfig.signing_secret` is always the current write key. `signing_key_id` identifies that key. `previous_signing_secrets` contains verification-only keys that remain active during a rotation window.

## Normal rotation

Use an overlap period so credentials created with the previous key remain valid until they naturally expire.

1. Keep the existing secret available under a stable previous key id.
2. Deploy the new secret as `signing_secret` with a new `signing_key_id`.
3. Put the old secret in `previous_signing_secrets`.
4. Keep both keys active for at least the maximum lifetime of any OTP challenge or refresh-session family that may still contain a hash created with the old key.
5. After the overlap period, remove the retired key from `previous_signing_secrets`.

Example:

```python
IdentityModuleConfig(
    ...,
    signing_secret=current_secret,
    signing_key_id="2026-08",
    previous_signing_secrets={
        "2026-07": previous_secret,
    },
)
```

Identity writes only with `2026-08` and can verify hashes written with either `2026-08` or `2026-07`.

## Legacy unversioned hashes

Hashes created before key identifiers were introduced contain only the hexadecimal digest. During migration, Identity verifies such hashes against every active HMAC key. This allows a rolling deployment without invalidating existing OTP challenges or refresh sessions.

Do not keep retired keys indefinitely. Once all credentials that could depend on a retired or legacy key have expired, remove that key from the active verification set.

## Compromised key

A compromised key is not a normal rotation. If an attacker may possess an HMAC key, assume credentials hashed with that key can be forged.

1. Replace the compromised key immediately.
2. Do not keep the compromised key in `previous_signing_secrets` merely to preserve session continuity.
3. Revoke affected active sessions, preferably using the existing bulk session-revocation capability.
4. Invalidate or allow existing OTP challenges to expire according to the incident response decision.
5. Review security events for suspicious OTP or refresh-token activity during the exposure window.

## Key management requirements

- Every HMAC secret must be at least 32 bytes.
- Key ids must be non-empty and must not contain `$`.
- Do not commit secrets to source control.
- Load current and previous keys from the host application's secret-management layer.
- Use distinct key ids for each rotation generation.
