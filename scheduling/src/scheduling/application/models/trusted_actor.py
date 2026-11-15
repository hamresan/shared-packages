"""Authenticated host actor with an authoritative tenant identity."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrustedActor:
    tenant_id: str
    actor_id: str

    def __post_init__(self) -> None:
        if not self.tenant_id.strip() or not self.actor_id.strip():
            raise ValueError("Trusted actor and tenant identifiers must be non-empty.")
