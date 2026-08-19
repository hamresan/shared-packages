# Identity Retention Cleanup

The identity package exposes `IdentityModule.data_retention_cleaner` and `IdentityPublicApi.data_retention_cleaner` for host-scheduled cleanup. The package intentionally does not create its own scheduler, worker, or cron process.

## Defaults

- OTP challenge retention: 7 days after expiration or consumption.
- Session retention: 30 days after expiration or revocation.
- Maximum deletes per table per execution: 500 rows.

All values are configurable through `IdentityModuleConfig`:

- `otp_challenge_retention`
- `session_retention`
- `retention_cleanup_batch_size`

## Scheduling

The host should call `await identity_module.data_retention_cleaner.execute()` from its existing cron, worker, or scheduler. A daily run is a reasonable baseline. Higher-volume deployments may run it more frequently.

Each execution is intentionally bounded. If more eligible rows exist than the configured batch size, subsequent executions continue deleting the oldest eligible rows.

## Safety

Cleanup deletes only:

- OTP challenges whose `expires_at` or `consumed_at` is older than the configured OTP cutoff.
- Sessions whose `expires_at` or `revoked_at` is older than the configured session cutoff.

Active OTP challenges and active sessions are not eligible for deletion.
