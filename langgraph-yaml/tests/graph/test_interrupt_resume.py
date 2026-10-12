"""Verify native LangGraph checkpoint interruption and resume behavior."""

# pyright: reportMissingTypeStubs=false

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

from langgraph_yaml import GraphBuilder, HandlerRegistry, RouterRegistry, parse_workflow


class ChoiceState(TypedDict):
    choice: str


def request_choice(state: ChoiceState) -> dict[str, str]:
    response = interrupt({"question": "Choose a product"})
    return {"choice": str(response)}


def test_interrupt_resume_uses_host_checkpointer_and_thread_id() -> None:
    definition = parse_workflow(
        """
schema_version: 1
name: choice_demo
start: request
nodes:
  request:
    handler: request_choice
edges:
  - from: request
    to: END
"""
    )
    saver = InMemorySaver()
    graph = GraphBuilder(
        definition=definition,
        state_schema=ChoiceState,
        handlers=HandlerRegistry({"request_choice": request_choice}),
        routers=RouterRegistry(),
    ).compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "test-customer-1"}}
    paused = graph.invoke({"choice": ""}, config=config)
    assert paused["__interrupt__"]
    resumed = graph.invoke(Command(resume="sku-1"), config=config)
    assert resumed["choice"] == "sku-1"
    assert graph.checkpointer is saver
