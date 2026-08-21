import os
from dataclasses import dataclass


DEFAULT_EXAMPLE_SIGNING_SECRET = b"identity-store-consumer-example-only-secret"


@dataclass(frozen=True, slots=True)
class ConsumerSettings:
    identity_signing_secret: bytes


def load_consumer_settings() -> ConsumerSettings:
    configured_secret = os.getenv("IDENTITY_SIGNING_SECRET")
    return ConsumerSettings(
        identity_signing_secret=(
            configured_secret.encode("utf-8")
            if configured_secret is not None
            else DEFAULT_EXAMPLE_SIGNING_SECRET
        )
    )
