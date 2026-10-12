"""Integration tests for native LangGraph workflow composition."""

from typing import TypedDict
from unittest.mock import patch

from langgraph.graph import StateGraph

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from langgraph_yaml.config.models import WorkflowDefinition
from langgraph_yaml.graph import GraphBuilder, GraphBuildError
from langgraph_yaml.registration import HandlerRegistry, RouterRegistry
from langgraph_yaml.validation import WorkflowValidationError


class State(TypedDict):
    count: int
    trace: list[str]


def increment(state: State) -> dict[str, object]:
    return {"count": state["count"] + 1, "trace": [*state["trace"], "step"]}


def finish(state: State) -> dict[str, object]:
    return {"trace": [*state["trace"], "finish"]}


def route(state: State) -> str:
    return "again" if state["count"] < 3 else "done"


def definition(edges: list[dict[str, object]]) -> WorkflowDefinition:
    return WorkflowDefinition.model_validate(
        {
            "schema_version": 1,
            "name": "example",
            "start": "step",
            "nodes": {
                "step": {"handler": "increment"},
                "finish": {"handler": "finish"},
            },
            "edges": edges,
        }
    )


def builder(
    edges: list[dict[str, object]],
    *,
    handlers: HandlerRegistry | None = None,
    routers: RouterRegistry | None = None,
) -> GraphBuilder:
    return GraphBuilder(
        definition=definition(edges),
        state_schema=State,
        handlers=handlers if handlers is not None else HandlerRegistry(
            {"increment": increment, "finish": finish}
        ),
        routers=routers if routers is not None else RouterRegistry({"route": route}),
    )


def test_direct_chain_invokes_real_langgraph() -> None:
    graph = builder(
        [{"from": "step", "to": "finish"}, {"from": "finish", "to": "END"}]
    ).compile()
    result = graph.invoke({"count": 0, "trace": []})
    assert result == {"count": 1, "trace": ["step", "finish"]}


def test_conditional_branch_and_loop() -> None:
    graph = builder(
        [
            {
                "from": "step",
                "router": "route",
                "routes": {"again": "step", "done": "finish"},
            },
            {"from": "finish", "to": "END"},
        ]
    ).compile()
    result = graph.invoke({"count": 0, "trace": []})
    assert result["count"] == 3
    assert result["trace"] == ["step", "step", "step", "finish"]


def test_compilation_is_repeatable() -> None:
    workflow_builder = builder(
        [{"from": "step", "to": "finish"}, {"from": "finish", "to": "END"}]
    )
    first = workflow_builder.compile()
    second = workflow_builder.compile()
    assert first is not second
    assert first.invoke({"count": 0, "trace": []}) == second.invoke(
        {"count": 0, "trace": []}
    )


def test_missing_handler_fails_before_graph_construction() -> None:
    workflow_builder = builder(
        [{"from": "step", "to": "finish"}, {"from": "finish", "to": "END"}],
        handlers=HandlerRegistry({"increment": increment}),
    )
    with pytest.raises(WorkflowValidationError, match="finish"):
        workflow_builder.compile()


def test_missing_router_fails_before_graph_construction() -> None:
    workflow_builder = builder(
        [
            {"from": "step", "router": "route", "routes": {"done": "finish"}},
            {"from": "finish", "to": "END"},
        ],
        routers=RouterRegistry(),
    )
    with pytest.raises(WorkflowValidationError, match="router"):
        workflow_builder.compile()


def test_checkpointer_is_forwarded() -> None:
    saver = InMemorySaver()
    graph = builder(
        [{"from": "step", "to": "finish"}, {"from": "finish", "to": "END"}]
    ).compile(checkpointer=saver)
    result = graph.invoke(
        {"count": 0, "trace": []},
        config={"configurable": {"thread_id": "test-thread"}},
    )
    assert result["count"] == 1
    assert graph.checkpointer is saver


def test_langgraph_compile_error_preserves_cause() -> None:
    workflow_builder = builder(
        [{"from": "step", "to": "finish"}, {"from": "finish", "to": "END"}]
    )
    with patch.object(
        StateGraph, "compile", side_effect=ValueError("compile rejected")
    ):
        with pytest.raises(GraphBuildError, match="example") as exc:
            workflow_builder.compile()
    assert isinstance(exc.value.__cause__, ValueError)
