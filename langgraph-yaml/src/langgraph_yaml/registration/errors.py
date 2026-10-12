"""Typed errors for explicitly configured callable registries."""


class RegistryError(ValueError):
    """Base error for invalid callable registry operations."""


class InvalidRegistrationError(RegistryError):
    """A registry name or implementation is invalid."""


class DuplicateRegistrationError(RegistryError):
    """A callable name is already registered."""


class UnknownRegistrationError(RegistryError, LookupError):
    """A requested callable has not been registered."""
