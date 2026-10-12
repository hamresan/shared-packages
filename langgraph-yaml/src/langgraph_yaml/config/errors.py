"""Errors raised at the YAML configuration loading boundary."""


class WorkflowLoadError(ValueError):
    """A workflow could not be read or parsed safely."""
