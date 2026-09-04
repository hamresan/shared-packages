# Examples

This directory contains small consumer examples for `hamresan-instagram-api`.

## Profile and media example

`profile_and_media.py` demonstrates the normal composition boundary:

```text
host-owned connection/token adapters
        ↓
Instagram application services
        ↓
Meta infrastructure providers
        ↓
Meta HTTP API
```

The example assumes Instagram authorization has already happened. In a real host application,
`InstagramConnectionReader` and `InstagramAccessTokenProvider` should normally be adapters over
the public contracts exposed by `hamresan-instagram-auth`. The example uses environment-backed
adapters only to keep the sample focused on this package.

Set:

```bash
export INSTAGRAM_CONNECTION_ID="your-local-connection-id"
export INSTAGRAM_ACCOUNT_ID="the-provider-instagram-account-id"
export INSTAGRAM_ACCESS_TOKEN="the-access-token-for-that-connection"
export META_API_VERSION="the-Graph-API-version-you-have-verified"
```

Then run from the `instagram_api` package directory:

```bash
python examples/profile_and_media.py
```

The code reads the selected profile and lists its owned media. Every operation carries the explicit
`InstagramConnectionId`; the sample does not introduce a global active Instagram account.

Do not commit access tokens or other Meta credentials. Production hosts should resolve tokens
through their authorization package/secret boundary instead of environment variables.
