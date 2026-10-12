# LangGraph YAML

A proposed configuration-driven Python package for building LangGraph `StateGraph` workflows from human-readable YAML, with behavior implemented exclusively by explicitly registered Python functions.

> **Status: Design stage — not implemented or installable yet.** All Python APIs below are proposed contracts and may be refined during implementation. This README is the first documentation deliverable.

## Overview

LangGraph already handles graph execution, runtime state, graph validation, checkpoints, interrupts, and persistence integrations. This package will focus only on YAML loading, validated declarative topology, and graph assembly. It is independent of any application or LLM provider.

### Intended first-release features

- Versioned YAML configuration (`schema_version: 1`).
- Named nodes, ordinary edges, labeled conditional routes, and `END`.
- Pydantic v2 configuration models and explicit errors for invalid configuration.
- Separate handler and router registries populated by the host application.
- A generic builder wrapping LangGraph `StateGraph`.
- Host-provided state schema, checkpointer, and store, where supported by the pinned LangGraph version.
- Deterministic execution, no arbitrary imports/evaluation from YAML.

Not planned: a new workflow runtime, scheduler, database, expression interpreter, dynamic plugin loader, visual editor, or admin UI.

## Example YAML

Create `sellora_sales.yaml`:

```yaml
schema_version: 1
name: sellora_sales
start: search_product

nodes:
  search_product:
    handler: search_product
  add_to_cart:
    handler: add_to_cart
  checkout:
    handler: checkout
  review_order:
    handler: review_order
  payment:
    handler: payment
  track_order:
    handler: track_order

edges:
  - from: search_product
    to: add_to_cart
  - from: add_to_cart
    router: after_cart
    routes:
      continue_shopping: search_product
      checkout: checkout
  - from: checkout
    to: review_order
  - from: review_order
    to: payment
  - from: payment
    to: track_order
  - from: track_order
    to: END
```

Node IDs are topology identifiers, **not** Python import paths. Each `handler` value resolves through the host-provided handler registry. Routers return declared **route keys**; YAML resolves those keys to destination node IDs (or `END`).

## Proposed Python API usage

The following is a **usage sketch, not executable code yet**. It shows how dependencies stay in Python and topology stays in YAML.

```python
from typing import TypedDict

from langgraph_yaml import GraphBuilder, HandlerRegistry, RouterRegistry, load_workflow


class SalesState(TypedDict):
    selections: list[str]
    selection_index: int
    cart: dict[str, int]
    payment_status: str
    tracking_status: str


def search_product(state: SalesState) -> dict:
    # A real example will inject a mock catalog and a finite selection sequence.
    return {"selection_index": state["selection_index"] + 1}


def add_to_cart(state: SalesState) -> dict:
    product_id = state["selections"][state["selection_index"] - 1]
    cart = dict(state["cart"])
    cart[product_id] = cart.get(product_id, 0) + 1
    return {"cart": cart}


def after_cart(state: SalesState) -> str:
    if state["selection_index"] < len(state["selections"]):
        return "continue_shopping"
    return "checkout"


def checkout(state: SalesState) -> dict:
    return {}


def review_order(state: SalesState) -> dict:
    return {}


def payment(state: SalesState) -> dict:
    return {"payment_status": "paid"}


def track_order(state: SalesState) -> dict:
    return {"tracking_status": "processing"}


definition = load_workflow("sellora_sales.yaml")

handlers = HandlerRegistry({
    "search_product": search_product,
    "add_to_cart": add_to_cart,
    "checkout": checkout,
    "review_order": review_order,
    "payment": payment,
    "track_order": track_order,
})
routers = RouterRegistry({"after_cart": after_cart})

graph = GraphBuilder(
    definition=definition,
    state_schema=SalesState,
    handlers=handlers,
    routers=routers,
).compile()

result = graph.invoke({
    "selections": ["sku-1", "sku-1", "sku-2"],
    "selection_index": 0,
    "cart": {},
    "payment_status": "pending",
    "tracking_status": "unknown",
})
# Intended cart result: {"sku-1": 2, "sku-2": 1}
# Loop: search -> cart -> search -> cart -> search -> cart -> checkout -> ...
```

This single invocation models a bounded deterministic demonstration, **not** a real customer journey across separate chat messages.

For a real application, use supported LangGraph interrupts, thread-scoped checkpointing, and resume functionality to pause for customer input. Integrate payment callbacks through the host application; do not treat payment approval as a synchronous in-graph operation.

## Proposed package structure

```text
langgraph-yaml/
├── README.md
├── pyproject.toml
├── src/langgraph_yaml/
│   ├── __init__.py
│   ├── config/
│   │   ├── models.py
│   │   └── loader.py
│   ├── registration/
│   │   ├── handlers.py
│   │   └── routers.py
│   ├── validation/
│   │   └── references.py
│   └── graph/
│       └── builder.py
├── examples/
│   ├── sellora_sales.yaml
│   └── sellora_mock.py
└── tests/
    ├── config/
    ├── registration/
    ├── validation/
    ├── graph/
    └── examples/
```

The final structure will be adjusted as necessary to preserve single responsibility and avoid unnecessary layers. Loading/parsing, validation, registration, and graph construction remain separate. LangGraph itself remains responsible for execution and graph-level validation.

## Development plan

1. Verify current LangGraph APIs, compatibility, and existing configuration-first tools; select pinned versions.
2. Define Pydantic config models, YAML loader, errors, and focused tests.
3. Implement explicit typed handler/router registries and tests.
4. Implement graph builder and compilation, relying on LangGraph validation where appropriate.
5. Build the executable Sellora mock with bounded repeated selections, assertions, trace, and final state.
6. Finalize packaging, documentation, installation instructions, and run pytest, Ruff, and a type checker.

**Each implementation stage requires review before proceeding to the next major stage.**

## Local installation (after implementation)

Once `pyproject.toml` and the source package exist:

```bash
cd langgraph-yaml
uv sync --extra dev
uv run pytest
make check
```

The distribution name, pinned dependency versions, release process, and optional PyPI publishing will be finalized during the packaging stage. No PyPI release or verified working implementation is claimed here.

## Engineering principles

Python 3.12+, LangGraph, Pydantic v2, PyYAML (or a documented alternative), pytest, Ruff, and static type checking. Clean architecture and SOLID: small components, explicit dependency injection, sensible package public exports, dedicated test fakes/factories, no execution of arbitrary YAML and no custom persistence or graph runtime.

## Development with uv

From `langgraph-yaml/`, install [uv](https://docs.astral.sh/uv/) and run:

```bash
uv sync --extra dev
uv lock
make check
```

`uv sync` creates and manages `.venv` and installs the project in editable mode. `uv run` ensures pytest, Ruff, and Pyright use the same environment instead of system Python. Commit the generated `uv.lock` once dependency resolution succeeds. Until then, `uv run` may resolve packages online and is not reproducible from a committed lockfile.

The `Makefile` runs checks and a wheel build using uv. The package's Python version is selected via `.python-version` (3.12).
