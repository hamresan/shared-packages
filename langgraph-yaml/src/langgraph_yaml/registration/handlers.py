"""Explicit dependency registry for LangGraph node handlers."""

from collections.abc import Callable, Mapping

from langgraph_yaml.registration.base import CallableRegistry

# LangGraph accepts different state/config/runtime callable signatures.
# Signature compatibility is checked when wiring the actual StateGraph.
Handler = Callable[..., object]


class HandlerRegistry(CallableRegistry[Handler]):
    """Resolve host-provided node handlers by their configured names."""

    def __init__(self, handlers: Mapping[str, Handler] | None = None) -> None:
        super().__init__(handlers, kind="handler")
