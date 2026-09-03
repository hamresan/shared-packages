"""Persistence errors exposed without SQLAlchemy details."""


class DuplicateInstagramConnectionError(Exception):
    """The same Instagram account is already connected for the same owner."""


class InstagramConnectionConcurrencyError(Exception):
    """A stale connection snapshot attempted to overwrite a newer update."""
