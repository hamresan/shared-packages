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

    def add_to_cart(self, state: SalesState) -> dict[str, object]:
        sku = state['pending_sku']
        if sku is None:
            raise ValueError('No selected SKU')
        cart = dict(state['cart'])
        cart[sku] = cart.get(sku, 0) + 1
        return {'cart': cart, 'pending_sku': None, 'trace': [*state['trace'], f'cart:{sku}']}

    def checkout(self, state: SalesState) -> dict[str, object]:
        return {'status': 'checkout', 'trace': [*state['trace'], 'checkout']}

    def review(self, state: SalesState) -> dict[str, object]:
        return {'status': 'reviewed', 'trace': [*state['trace'], 'review']}

    def payment(self, state: SalesState) -> dict[str, object]:
        return {'status': 'paid_mock', 'trace': [*state['trace'], 'payment:mock']}

    def tracking(self, state: SalesState) -> dict[str, object]:
        return {'status': 'tracked_mock', 'tracking_id': 'DEMO-0001', 'trace': [*state['trace'], 'tracking']}
