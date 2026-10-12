"""RouterRegistry behavior and error cases."""

import pytest

from langgraph_yaml.registration import (
    DuplicateRegistrationError,
    InvalidRegistrationError,
    RouterRegistry,
    UnknownRegistrationError,
)


def router(state: object) -> str:
    return "done"


class CallableRouter:
    def __call__(self, state: object) -> str:
        return "done"


def test_resolves_router() -> None:
    assert RouterRegistry({"branch": router}).resolve("branch") is router


def test_accepts_callable_object() -> None:
    implementation = CallableRouter()
    registry = RouterRegistry({"branch": implementation})
    assert registry.resolve("branch") is implementation


def test_register_router() -> None:
    registry = RouterRegistry()
    registry.register("branch", router)
    assert registry.resolve("branch") is router


def test_duplicate_router_is_rejected() -> None:
    registry = RouterRegistry({"branch": router})
    with pytest.raises(DuplicateRegistrationError):
        registry.register("branch", router)


def test_invalid_router_name_is_rejected() -> None:
    with pytest.raises(InvalidRegistrationError):
        RouterRegistry({" ": router})


def test_non_callable_router_is_rejected() -> None:
    with pytest.raises(InvalidRegistrationError):
        RouterRegistry({"branch": 42})  # type: ignore[arg-type]


def test_unknown_router_is_actionable() -> None:
    with pytest.raises(UnknownRegistrationError, match="branch"):
        RouterRegistry({"branch": router}).resolve("other")


def test_names_are_deterministic() -> None:
    assert RouterRegistry({"z": router, "a": router}).names() == ("z", "a")
