# Identity Index Migration Notes

## L-6 — OTP active/latest lookup

The identity package defines this composite index for the OTP hot path:

`ix_identity_otp_challenges_destination_purpose_created_at`

Columns, in order:

1. `normalized_destination`
2. `purpose`
3. `created_at`

This matches the leading equality predicates and ordering used by `get_latest_active()`.

Hosts that manage schema changes with Alembic or another migration tool must add the equivalent database index when deploying this version. Updating SQLAlchemy model metadata alone does not modify an existing production schema.

Example SQL shape:

```sql
CREATE INDEX ix_identity_otp_challenges_destination_purpose_created_at
ON identity_otp_challenges (normalized_destination, purpose, created_at);
```

Keep the existing single-column indexes for now. Removing them should be based on production query plans and workload measurements rather than assumption, because they also support cleanup and other lookup paths.
