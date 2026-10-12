"""Run the deterministic Sellora example."""

from pathlib import Path
from typing import Any, TypedDict

from langgraph_yaml.config.loader import load_workflow
from langgraph_yaml.graph import GraphBuilder
from langgraph_yaml.registration import HandlerRegistry, RouterRegistry


class SalesState(TypedDict):
    selections: list[str]
    cursor: int
    pending_sku: str | None
    cart: dict[str, int]
    status: str
    trace: list[str]
    tracking_id: str | None
