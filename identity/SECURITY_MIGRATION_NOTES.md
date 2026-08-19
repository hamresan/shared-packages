# Identity Security Migration Notes

## Absolute refresh-family lifetime

The refresh-family lifetime hardening adds the non-null `family_expires_at` column to `identity_sessions`.

Identity intentionally does not ship its own Alembic revision history. The host application must generate and apply this schema change in its existing migration graph.

### Existing rows

For existing sessions, use a security-conservative backfill before making the column non-null:

```sql
UPDATE identity_sessions
SET family_expires_at = expires_at
WHERE family_expires_at IS NULL;
```

This prevents an existing refresh-token family from gaining additional lifetime during migration. After the backfill, make `family_expires_at` non-null and add the index represented by the SQLAlchemy model.

### New sessions

New root sessions receive `family_expires_at = created_at + session_absolute_ttl`. Rotated sessions inherit the exact same `family_expires_at`, and their own expiration is capped at that boundary.

The default configuration is:

- `session_ttl = 30 days`
- `session_absolute_ttl = 90 days`

Hosts can override both values through `IdentityModuleConfig`.
