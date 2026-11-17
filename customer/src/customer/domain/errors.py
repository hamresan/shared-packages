"""Typed customer-domain and application errors."""


class CustomerError(Exception):
    """Base exception for expected Customer failures."""


class CustomerNotFoundError(CustomerError):
    """Missing or inaccessible customer; do not disclose tenant existence."""


class CustomerPermissionDeniedError(CustomerError):
    """A trusted actor is not allowed to perform the action."""


class CustomerValidationError(CustomerError):
    """Invalid customer command or query input."""


class CustomerVersionConflictError(CustomerError):
    """Optimistic version check failed."""


class CustomerInvalidStateError(CustomerError):
    """Invalid customer lifecycle transition."""


class CustomerErasedError(CustomerInvalidStateError):
    """Operation attempted against terminally erased customer."""


class CustomerIdempotencyConflictError(CustomerError):
    """Same idempotency key was used for materially different creation inputs."""


class CustomerIdentityConflictError(CustomerError):
    """A verified identity is already actively linked to another customer."""


class CustomerIdentityVerificationError(CustomerError):
    """The host did not provide acceptable identity verification evidence."""
