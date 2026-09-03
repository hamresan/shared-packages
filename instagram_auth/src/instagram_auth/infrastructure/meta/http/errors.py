"""Transport-level failures without request secrets."""


class MetaTransportError(Exception):
    """Represent a non-timeout transport failure."""


class MetaTransportTimeoutError(MetaTransportError):
    """Represent a provider request timeout."""
