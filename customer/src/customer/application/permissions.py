"""Customer-owned operation names; role mappings remain host-owned."""

from enum import StrEnum


class CustomerPermission(StrEnum):
    READ = "customer.read"
    CREATE = "customer.create"
    UPDATE = "customer.update"
    ARCHIVE = "customer.archive"
    ERASE = "customer.erase"
    NOTES_READ = "customer.notes.read"
    NOTES_WRITE = "customer.notes.write"
    IDENTITY_LINK = "customer.identity.link"
    IDENTITY_RESOLVE = "customer.identity.resolve"
    EXTERNAL_IDENTITY_MANAGE = "customer.external_identity.manage"
    EXTERNAL_IDENTITY_LOOKUP = "customer.external_identity.lookup"
