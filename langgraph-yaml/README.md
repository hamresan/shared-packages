# LangGraph YAML

Build native LangGraph `StateGraph` workflows from validated, declarative YAML.
Python handlers and routers are registered explicitly by the host application;
YAML cannot import Python code or execute expressions.

**Status:** development release `0.1.0.dev0` (not published).

## Compatibility

| Component | Supported configuration |
| --- | --- |
| Python | 3.12+ |
| LangGraph | exactly 1.2.14 |
| Pydantic | 2.12.x or later, below 3 |
| PyYAML | 6.0.3 or later, below 7 |

LangGraph is pinned to preserve the validated graph compilation API. Other
dependency ranges are intentionally bounded by major version. The repository
does not currently commit `uv.lock`; installs resolve within those ranges.

## Installation and development

From the `langgraph-yaml` directory:

```bash
uv sync --extra dev
make check
uv run --extra dev python examples/sellora_mock.py
```

Install the local package into another environment with
`uv pip install ./langgraph-yaml` from the monorepo root. No PyPI
distribution is claimed.

## Supported topology and public API

The public imports are `load_workflow`, `parse_workflow`,
`WorkflowDefinition`, `HandlerRegistry`, `RouterRegistry`,
`WorkflowReferenceValidator`, `GraphBuilder`, and the corresponding
configuration, validation, and graph build errors.

A minimal configuration:

```yaml
schema_version: 1
name: hello
start: greet
nodes:
  greet:
    handler: greet
edges:
  - from: greet
    to: END
```

Store that YAML as `hello.yaml`, then compose it in Python:

```python
from typing import TypedDict

from langgraph_yaml import GraphBuilder, HandlerRegistry, RouterRegistry, load_workflow


class State(TypedDict):
    message: str


def greet(state: State) -> dict[str, str]:
    return {"message": "Hello from LangGraph"}


definition = load_workflow("hello.yaml")
graph = GraphBuilder(
    definition=definition,
    state_schema=State,
    handlers=HandlerRegistry({"greet": greet}),
    routers=RouterRegistry(),
).compile()

assert graph.invoke({"message": ""})["message"] == "Hello from LangGraph"
```

The loader validates the YAML schema; `GraphBuilder.compile()` performs
reference validation before assembling the native LangGraph graph. Node
identifiers and registry names are distinct: handlers and routers must be
explicitly supplied. Conditional edges map router-returned keys to destination
node IDs or `END`.

For a real branching and looping example, see
[`examples/sellora_workflow.yaml`](examples/sellora_workflow.yaml) and
[`examples/sellora_mock.py`](examples/sellora_mock.py).
That example runs a finite synthetic selection sequence in **one invocation**,
not an interactive customer conversation. Mock payment and tracking do not
contact external systems.

## Runtime ownership: customer input and interrupts

`langgraph-yaml` only composes a graph. The **host application** owns
conversation transport, authentication, authorization, durable checkpoints,
thread identifiers, retries, and external side effects.

For a real multi-message conversation, a host-registered node can call
LangGraph's `interrupt()` to request customer input. Compile with a
host-provided checkpointer, invoke with a stable per-conversation
`configurable.thread_id`, persist that thread identifier, and resume with
`Command(resume=...)`. A minimal host-side pattern using the pinned
LangGraph API:

```python
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

from langgraph_yaml import GraphBuilder, HandlerRegistry, RouterRegistry, parse_workflow


class State(TypedDict):
    choice: str


def request_choice(state: State) -> dict[str, str]:
    answer = interrupt({"question": "Choose a product"})
    return {"choice": str(answer)}


definition = parse_workflow("""
schema_version: 1
name: choice_demo
start: request
nodes:
  request:
    handler: request_choice
edges:
  - from: request
    to: END
""")

graph = GraphBuilder(
    definition=definition,
    state_schema=State,
    handlers=HandlerRegistry({"request_choice": request_choice}),
    routers=RouterRegistry(),
).compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "example-conversation-1"}}
paused = graph.invoke({"choice": ""}, config=config)
assert paused["__interrupt__"]
resumed = graph.invoke(Command(resume="sku-1"), config=config)
assert resumed["choice"] == "sku-1"
```

`InMemorySaver` is for demos/tests; production must use an appropriate
durable LangGraph checkpointer. Interrupts can replay node execution on
resume: place irreversible effects outside replayable code or guard them with
host-managed idempotency. Do not assume a single graph invocation spans
multiple inbound customer messages.

## Payment and external integration boundaries

A production payment provider and its webhooks belong to the **host**:
the host creates payment intents/links, verifies provider signatures,
deduplicates callbacks using stable provider event/transaction identifiers,
persists payment transitions transactionally, and resumes the appropriate
conversation thread only after verified payment state is recorded.
Replayed graph nodes must not duplicate charges, orders, or notifications.
The package does not implement payment processing, webhook validation,
idempotency storage, or event transport.

## Errors and diagnostics

- `WorkflowLoadError`: invalid YAML, duplicate keys, unsafe tags,
  unsupported schema data, or unreadable UTF-8 file. Error includes source.
- `WorkflowValidationError`: unknown handlers/routers, invalid topology
  references, conflicting outgoing edges, or missing required edges.
- `GraphBuildError`: native LangGraph graph construction/compile failure;
  the original exception is preserved as the cause.

Errors are raised during loading or compilation, not silently ignored.

## Quality and packaging

```bash
make lint
make typecheck
make coverage
make wheel-smoke
make check
```

`make check` runs Ruff checks and formatting verification, strict Pyright,
pytest with line coverage, wheel build, and an import smoke test. Before
publishing, inspect `dist/` wheel contents for `py.typed`, install the wheel
into a clean environment, verify the sdist if one is built, and review the
distribution name, dependency pin, changelog, license, and release credentials.
**No publication is performed by these commands.**

## Out of scope

This library does not provide a workflow runner, scheduler, database, state
storage implementation, visual editor, dynamic import system, commerce
integration, or arbitrary expression interpreter. Native LangGraph remains
responsible for graph execution, interrupts, and checkpoint behavior.
