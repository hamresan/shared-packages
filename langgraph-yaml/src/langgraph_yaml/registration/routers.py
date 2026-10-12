"""Explicit dependency registry for LangGraph conditional edge routers."""

from collections.abc import Callable, Mapping

from langgraph_yaml.registration.base import CallableRegistry

# LangGraph routers may accept state and optional runtime/config parameters.
# Route result compatibility is checked at graph composition/runtime boundaries.
Router = Callable[..., object]


class RouterRegistry(CallableRegistry[Router]):
    """Resolve host-provided conditional routers by configured names."""

    def __init__(self, routers: Mapping[str, Router] | None = None) -> None:
        super().__init__(routers, kind="router")
