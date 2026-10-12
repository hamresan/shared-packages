"""Tests for strict workflow configuration definitions."""

import pytest
from pydantic import ValidationError

from langgraph_yaml.config import (
    ConditionalEdge,
    DirectEdge,
    WorkflowDefinition,
)


def valid_definition() -> dict[str, object]:
    return {
        "schema_version": 1,
        "name": "sales",
        "start": "search",
        "nodes": {
            "search": {"handler": "search_products"},
            "cart": {"handler": "add_to_cart"},
        },
        "edges": [
            {"from": "search", "to": "cart"},
            {
                "from": "cart",
                "router": "next_step",
                "routes": {"again": "search", "done": "END"},
            },
        ],
    }


def test_valid_direct_conditional_and_cyclic_edges() -> None:
    definition = WorkflowDefinition.model_validate(valid_definition())
    assert isinstance(definition.edges[0], DirectEdge)
    assert isinstance(definition.edges[1], ConditionalEdge)
    assert definition.edges[0].source == "search"
    assert definition.edges[1].routes["again"] == "search"


def test_models_are_immutable() -> None:
    definition = WorkflowDefinition.model_validate(valid_definition())
    with pytest.raises(ValidationError):
        definition.name = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", 2),
        ("schema_version", "1"),
        ("name", ""),
        ("name", "  "),
        ("start", ""),
        ("nodes", {}),
        ("nodes", {"END": {"handler": "handler"}}),
        ("nodes", {"START": {"handler": "handler"}}),
        ("nodes", {"search": {"handler": ""}}),
        ("nodes", {"search": {"handler": "  "}}),
        ("nodes", {"search": {"handler": "handler", "extra": True}}),
    ],
)
def test_invalid_fields_are_rejected(field: str, value: object) -> None:
    data = valid_definition()
    data[field] = value
    with pytest.raises(ValidationError) as exc:
        WorkflowDefinition.model_validate(data)
    assert field in str(exc.value)


@pytest.mark.parametrize("field", ["name", "start", "nodes", "schema_version"])
def test_required_fields(field: str) -> None:
    data = valid_definition()
    del data[field]
    with pytest.raises(ValidationError) as exc:
        WorkflowDefinition.model_validate(data)
    assert field in str(exc.value)


@pytest.mark.parametrize(
    "edge",
    [
        {"from": "search"},
        {"from": "search", "to": "cart", "router": "next"},
        {"from": "search", "router": "next", "routes": {"go": "cart"}, "to": "cart"},
        {"from": "search", "router": "next", "routes": {}},
        {"from": "search", "router": "", "routes": {"go": "cart"}},
        {"from": "search", "router": "next", "routes": {"": "cart"}},
        {"from": "search", "router": "next", "routes": {"go": ""}},
        {"from": "search", "to": "START"},
        {"from": "search", "router": "next", "routes": {"go": "START"}},
        {"from": "search", "to": 123},
        {"from": "search", "to": "cart", "unknown": 1},
        {"from": "", "to": "cart"},
    ],
)
def test_invalid_edges_are_rejected(edge: dict[str, object]) -> None:
    data = valid_definition()
    data["edges"] = [edge]
    with pytest.raises(ValidationError) as exc:
        WorkflowDefinition.model_validate(data)
    assert "edges" in str(exc.value)


def test_unknown_top_level_field_is_rejected() -> None:
    data = valid_definition()
    data["unexpected"] = "value"
    with pytest.raises(ValidationError) as exc:
        WorkflowDefinition.model_validate(data)
    assert "unexpected" in str(exc.value)


def test_missing_edges_defaults_to_empty_tuple() -> None:
    data = valid_definition()
    del data["edges"]
    definition = WorkflowDefinition.model_validate(data)
    assert definition.edges == ()


def test_invalid_node_id_type_is_rejected() -> None:
    data = valid_definition()
    data["nodes"] = {7: {"handler": "search"}}
    with pytest.raises(ValidationError):
        WorkflowDefinition.model_validate(data)
