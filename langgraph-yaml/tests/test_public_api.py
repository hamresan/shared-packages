"""Smoke test the package's controlled public API."""

from langgraph_yaml import (
    GraphBuilder,
    HandlerRegistry,
    RouterRegistry,
    WorkflowDefinition,
    load_workflow,
    parse_workflow,
)


def test_public_api_exposes_real_components() -> None:
    assert GraphBuilder.__name__ == "GraphBuilder"
    assert HandlerRegistry.__name__ == "HandlerRegistry"
    assert RouterRegistry.__name__ == "RouterRegistry"
    assert WorkflowDefinition.__name__ == "WorkflowDefinition"
    assert callable(load_workflow)
    assert callable(parse_workflow)
