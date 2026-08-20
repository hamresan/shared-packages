# Identity model semantics

This note documents fields reviewed during security finding L-4 so persisted members are not mistaken for implemented behavior they do not provide.

## UserIdentity.value and normalized_value

`normalized_value` is the canonical value used for lookup, uniqueness, abuse-control keys, and authentication behavior.

`value` is retained as a persisted display/audit snapshot for schema compatibility. Identity logic must not use it for equality, uniqueness, rate limiting, or authentication decisions.

## OtpChallenge.destination_snapshot

`normalized_destination` is the canonical destination used by OTP lookup and security controls.

`destination_snapshot` is retained as the challenge-time destination snapshot for schema compatibility and audit/debugging. It must not be used as an alternate lookup or security key.

## User.updated_at

`updated_at` is persisted metadata for future user-state/profile mutations. The current package has limited user mutation behavior, so callers must not infer that it changes on every authentication event.

## Session.last_used_at

`last_used_at` records refresh-token use for a session when that session is successfully rotated. It is not updated during ordinary access-token validation and therefore must not be treated as a complete or authoritative record of user/session activity.

## Authorization scope

Identity authenticates users and validates sessions. It does not currently own authorization policy or permission evaluation. `AuthenticatedPrincipal` therefore contains identity/session authentication data only and intentionally has no permissions collection.
