"""Normalized Instagram customer profile models."""

from dataclasses import dataclass

from .identifiers import InstagramUserId


@dataclass(frozen=True, slots=True)
class InstagramCustomerProfile:
    """Provider-neutral profile for an Instagram messaging customer."""

    id: InstagramUserId
    username: str | None = None
    name: str | None = None
    profile_picture_url: str | None = None
