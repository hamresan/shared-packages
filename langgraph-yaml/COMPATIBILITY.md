# Compatibility and reuse decision

## Baseline

- Python >=3.12; local smoke tests used Python 3.13.
- LangGraph pinned to 1.2.14 for the first implementation baseline.
- Pydantic >=2.12,<3; PyYAML >=6.0.3,<7.
- pytest, Ruff, Pyright strict; a reproducible lockfile awaits successful resolution.

## Existing APIs to reuse

LangGraph StateGraph supports add_node, add_edge, add_conditional_edges,
set_entry_point / START, END, validate and compile. In 1.2.14 compile accepts
checkpointer, cache, store, interrupt_before, interrupt_after, debug, name,
and transformers. Only justified supported options should be exposed later.
Use context_schema rather than deprecated config_schema.

## Reuse versus custom layer

Reuse LangGraph for runtime, graph validation, state updates, checkpointing and
interrupts. Native LangGraph uses imperative Python graph assembly; the
requested strict YAML topology plus explicitly injected callable registries
requires only a thin declarative adapter. Do not build a new runtime, scheduler,
persistence implementation, expression interpreter or plugin loader. Recheck
mature YAML-to-LangGraph libraries before Stage 06.

## Stage 01 test status

Local installation was blocked because the environment cannot resolve pypi.org.
Running PYTHONPATH=src pytest -q yielded 1 passed and 1 failed:
the metadata test requires an installed distribution. Ruff and Pyright are
not installed in the available environment. This stage is **blocked**, not
accepted; rerun all quality gates with dependencies installed before PR.

## Sources

- https://reference.langchain.com/python/langgraph/graph/state/StateGraph
- https://reference.langchain.com/python/langgraph/graph/state/StateGraph/compile
- https://reference.langchain.com/python/langgraph/types/interrupt
- https://pypi.org/project/langgraph/1.2.14/
