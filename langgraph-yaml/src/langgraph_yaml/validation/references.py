"""Prevalidate workflow references without constructing a LangGraph graph."""

from langgraph_yaml.config.models import (
    ConditionalEdge,
    WorkflowDefinition,
)
from langgraph_yaml.registration import (
    HandlerRegistry,
    RouterRegistry,
    UnknownRegistrationError,
)
from langgraph_yaml.validation.errors import WorkflowValidationError


class WorkflowReferenceValidator:
    """Validate references and v1 outgoing-edge constraints."""

    def validate(
        self,
        definition: WorkflowDefinition,
        handlers: HandlerRegistry,
        routers: RouterRegistry,
    ) -> None:
        """Fail deterministically on the first invalid workflow reference."""
        workflow = definition.name
        nodes = definition.nodes

        if definition.start not in nodes:
            raise WorkflowValidationError(
                f"Workflow {workflow!r}: start node {definition.start!r} is undefined"
            )

        for node_id, node in nodes.items():
            try:
                handlers.resolve(node.handler)
            except UnknownRegistrationError as exc:
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}, node {node_id!r}: "
                    f"handler {node.handler!r} is not registered"
                ) from exc

        outgoing: set[str] = set()
        for edge in definition.edges:
            source = edge.source
            if source == "END":
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}: END cannot be an edge source"
                )
            if source not in nodes:
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}: edge source {source!r} is undefined"
                )
            if source in outgoing:
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}, node {source!r}: "
                    "multiple outgoing edge definitions"
                )
            outgoing.add(source)

            if isinstance(edge, ConditionalEdge):
                try:
                    routers.resolve(edge.router)
                except UnknownRegistrationError as exc:
                    raise WorkflowValidationError(
                        f"Workflow {workflow!r}, node {source!r}: "
                        f"router {edge.router!r} is not registered"
                    ) from exc
                for route_key, destination in edge.routes.items():
                    if destination != "END" and destination not in nodes:
                        raise WorkflowValidationError(
                            f"Workflow {workflow!r}, node {source!r}, "
                            f"route {route_key!r}: "
                            f"destination {destination!r} is undefined"
                        )
            elif edge.to != "END" and edge.to not in nodes:
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}, node {source!r}: "
                    f"destination {edge.to!r} is undefined"
                )

        for node_id in nodes:
            if node_id not in outgoing:
                raise WorkflowValidationError(
                    f"Workflow {workflow!r}, node {node_id!r}: "
                    "missing outgoing edge; use an explicit edge to END"
                )
