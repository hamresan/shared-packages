"""Compose validated YAML topology into LangGraph's native StateGraph."""

# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false

from collections.abc import Hashable
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore

from langgraph_yaml.config.models import ConditionalEdge, WorkflowDefinition
from langgraph_yaml.graph.errors import GraphBuildError
from langgraph_yaml.registration import HandlerRegistry, RouterRegistry
from langgraph_yaml.validation import WorkflowReferenceValidator


class GraphBuilder:
    """Build native LangGraph graphs from explicit, injected dependencies."""

    def __init__(
        self,
        *,
        definition: WorkflowDefinition,
        state_schema: type[Any],
        handlers: HandlerRegistry,
        routers: RouterRegistry,
        validator: WorkflowReferenceValidator | None = None,
    ) -> None:
        self.definition = definition
        self.state_schema = state_schema
        self.handlers = handlers
        self.routers = routers
        self.validator = validator or WorkflowReferenceValidator()

    def compile(
        self,
        *,
        checkpointer: BaseCheckpointSaver[Any] | None = None,
        store: BaseStore | None = None,
    ) -> Any:
        """Validate, construct and compile the native LangGraph workflow."""
        self.validator.validate(self.definition, self.handlers, self.routers)
        try:
            graph = StateGraph(self.state_schema)
            for node_id, node in self.definition.nodes.items():
                graph.add_node(node_id, self.handlers.resolve(node.handler))
            graph.add_edge(START, self.definition.start)
            for edge in self.definition.edges:
                if isinstance(edge, ConditionalEdge):
                    destinations: dict[Hashable, str] = {
                        route: END if target == "END" else target
                        for route, target in edge.routes.items()
                    }
                    graph.add_conditional_edges(
                        edge.source,
                        self.routers.resolve(edge.router),
                        destinations,
                    )
                else:
                    graph.add_edge(
                        edge.source,
                        END if edge.to == "END" else edge.to,
                    )
            return graph.compile(checkpointer=checkpointer, store=store)
        except (ValueError, TypeError, KeyError) as exc:
            raise GraphBuildError(
                f"Workflow {self.definition.name!r}: LangGraph build failed: {exc}"
            ) from exc
