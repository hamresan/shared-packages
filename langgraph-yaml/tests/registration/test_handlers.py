"""HandlerRegistry behavior and error cases."""

from collections.abc import Callable

import pytest

from langgraph_yaml.registration import (
    DuplicateRegistrationError,
    HandlerRegistry,
    InvalidRegistrationError,
    UnknownRegistrationError,
)


def handler(state: object) -> object:
    return state


class CallableHandler:
    def __call__(self, state: object) -> object:
        return state


def test_resolves_injected_handler() -> None:
    registry = HandlerRegistry({"step": handler})
    assert registry.resolve("step") is handler


def test_accepts_callable_object() -> None:
    implementation = CallableHandler()
    assert HandlerRegistry({"step": implementation}).resolve("step") is implementation


def test_snapshot_is_independent_of_input_mapping() -> None:
    handlers: dict[str, Callable[..., object]] = {"step": handler}
    registry = HandlerRegistry(handlers)
    handlers["other"] = handler
    assert registry.names() == ("step",)


def test_register_and_resolve() -> None:
    registry = HandlerRegistry()
    registry.register("step", handler)
    assert registry.resolve("step") is handler


def test_register_duplicate_is_rejected() -> None:
    registry = HandlerRegistry({"step": handler})
    with pytest.raises(DuplicateRegistrationError, match="already registered"):
        registry.register("step", handler)


@pytest.mark.parametrize("name", ["", " ", "\t"])
def test_empty_name_is_rejected(name: str) -> None:
    with pytest.raises(InvalidRegistrationError, match="non-empty"):
        HandlerRegistry({name: handler})


def test_non_callable_is_rejected() -> None:
    with pytest.raises(InvalidRegistrationError, match="callable"):
        HandlerRegistry({"step": 42})  # type: ignore[arg-type]


def test_unknown_name_is_actionable() -> None:
    registry = HandlerRegistry({"existing": handler})
    with pytest.raises(UnknownRegistrationError, match="existing"):
        registry.resolve("missing")


def test_names_preserve_insertion_order() -> None:
    registry = HandlerRegistry({"b": handler, "a": handler})
    assert registry.names() == ("b", "a")


def test_independent_registries() -> None:
    first = HandlerRegistry({"a": handler})
    second = HandlerRegistry({"b": handler})
    first.register("c", handler)
    assert second.names() == ("b",)
