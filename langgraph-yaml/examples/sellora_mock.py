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


class Catalog:
    def __init__(self, skus: frozenset[str]) -> None:
        self.skus = skus

    def contains(self, sku: str) -> bool:
        return sku in self.skus


class SalesHandlers:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog


    def search(self, state: SalesState) -> dict[str, object]:
        cursor = state['cursor']
        selections = state['selections']
        if cursor == len(selections):
            return {'pending_sku': None, 'trace': [*state['trace'], 'search:done']}
        sku = selections[cursor]
        if not self.catalog.contains(sku):
            raise ValueError(f'Unknown catalog SKU: {sku}')
        return {'cursor': cursor + 1, 'pending_sku': sku, 'trace': [*state['trace'], f'search:{sku}']}
