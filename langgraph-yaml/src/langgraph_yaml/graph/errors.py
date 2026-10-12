"""Errors raised while assembling or compiling a LangGraph workflow."""


class GraphBuildError(ValueError):
    """LangGraph could not build or compile a validated workflow."""
