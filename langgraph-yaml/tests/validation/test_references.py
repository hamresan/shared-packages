"""Workflow reference and topology validation tests."""

import pytest

from langgraph_yaml.config.models import WorkflowDefinition
from langgraph_yaml.registration import HandlerRegistry, RouterRegistry
from langgraph_yaml.validation import (
    WorkflowReferenceValidator,
    WorkflowValidationError,
)


def step(state: object) -> object:
    return state


def choose(state: object) -> str:
    return "done"


def workflow(
    *,
    start: str = "search",
    edges: list[dict[str, object]] | None = None,
    nodes: dict[str, dict[str, str]] | None = None,
) -> WorkflowDefinition:
    return WorkflowDefinition.model_validate(
        {
            "schema_version": 1,
            "name": "sales",
            "start": start,
            "nodes": nodes
            if nodes is not None
            else {
                "search": {"handler": "search_handler"},
                "checkout": {"handler": "checkout_handler"},
            },
            "edges": edges
            if edges is not None
            else [
                {"from": "search", "to": "checkout"},
                {"from": "checkout", "to": "END"},
            ],
        }
    )


def validate(
    definition: WorkflowDefinition,
    *,
    handlers: HandlerRegistry | None = None,
    routers: RouterRegistry | None = None,
) -> None:
    WorkflowReferenceValidator().validate(
        definition,
        handlers
        if handlers is not None
        else HandlerRegistry({"search_handler": step, "checkout_handler": step}),
        routers if routers is not None else RouterRegistry({"choose": choose}),
    )


def test_valid_direct_edges_and_terminal() -> None:
    validate(workflow())


def test_missing_start_node() -> None:
    with pytest.raises(WorkflowValidationError, match="start node 'missing'"):
        validate(workflow(start="missing"))


def test_missing_handler_identifies_node() -> None:
    with pytest.raises(WorkflowValidationError, match="node 'checkout'.*handler"):
        validate(workflow(), handlers=HandlerRegistry({"search_handler": step}))


def test_missing_router_identifies_source() -> None:
    definition = workflow(
        edges=[
            {
                "from": "search",
                "router": "unknown",
                "routes": {"done": "checkout"},
            },
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="router 'unknown'"):
        validate(definition)


def test_unknown_source() -> None:
    definition = workflow(
        edges=[
            {"from": "missing", "to": "checkout"},
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="source 'missing'"):
        validate(definition)


def test_end_cannot_be_source() -> None:
    definition = workflow(
        edges=[
            {"from": "END", "to": "checkout"},
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="END cannot"):
        validate(definition)


def test_unknown_direct_destination() -> None:
    definition = workflow(
        edges=[
            {"from": "search", "to": "missing"},
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="destination 'missing'"):
        validate(definition)


def test_unknown_conditional_destination_identifies_route() -> None:
    definition = workflow(
        edges=[
            {
                "from": "search",
                "router": "choose",
                "routes": {"done": "missing"},
            },
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(
        WorkflowValidationError, match="route 'done'.*destination 'missing'"
    ):
        validate(definition)


def test_duplicate_outgoing_source_is_rejected() -> None:
    definition = workflow(
        edges=[
            {"from": "search", "to": "checkout"},
            {"from": "search", "to": "END"},
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="multiple outgoing"):
        validate(definition)


def test_mixed_direct_and_conditional_outgoing_is_rejected() -> None:
    definition = workflow(
        edges=[
            {"from": "search", "to": "checkout"},
            {"from": "search", "router": "choose", "routes": {"done": "END"}},
            {"from": "checkout", "to": "END"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="multiple outgoing"):
        validate(definition)


def test_missing_terminal_edge_is_rejected() -> None:
    definition = workflow(edges=[{"from": "search", "to": "checkout"}])
    with pytest.raises(WorkflowValidationError, match="missing outgoing edge"):
        validate(definition)


def test_intentional_loop_is_allowed() -> None:
    definition = workflow(
        edges=[
            {"from": "search", "to": "checkout"},
            {
                "from": "checkout",
                "router": "choose",
                "routes": {"again": "search", "done": "END"},
            },
        ]
    )
    validate(definition)


def test_multiple_route_keys_can_share_destination() -> None:
    definition = workflow(
        edges=[
            {
                "from": "search",
                "router": "choose",
                "routes": {"yes": "checkout", "also_yes": "checkout"},
            },
            {"from": "checkout", "to": "END"},
        ]
    )
    validate(definition)


def test_node_id_differs_from_handler_and_route_key() -> None:
    definition = workflow(
        edges=[
            {
                "from": "search",
                "router": "choose",
                "routes": {"continue": "checkout"},
            },
            {"from": "checkout", "to": "END"},
        ]
    )
    validate(definition)


def test_first_error_is_deterministic() -> None:
    definition = workflow(
        edges=[
            {"from": "search", "to": "missing_a"},
            {"from": "checkout", "to": "missing_b"},
        ]
    )
    with pytest.raises(WorkflowValidationError, match="missing_a"):
        validate(definition)
