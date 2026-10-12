"""Errors raised for invalid workflow references and topology."""


class WorkflowValidationError(ValueError):
    """A workflow contains invalid references or outgoing edge definitions."""
