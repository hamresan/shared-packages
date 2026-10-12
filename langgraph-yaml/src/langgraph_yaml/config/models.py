"""Strict, immutable schema for version 1 workflow definitions."""

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    field_validator,
    model_validator,
)

NonEmptyString = Annotated[StrictStr, Field(min_length=1, pattern=r"\S")]
NodeId = NonEmptyString


class StrictDefinition(BaseModel):
    """Reject unknown fields and prevent mutation after validation."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class NodeDefinition(StrictDefinition):
    handler: NonEmptyString


class DirectEdge(StrictDefinition):
    source: NonEmptyString = Field(alias="from")
    to: NonEmptyString

    @model_validator(mode="after")
    def validate_target(self) -> "DirectEdge":
        if self.to == "START":
            raise ValueError("START cannot be an edge destination")
        return self


class ConditionalEdge(StrictDefinition):
    source: NonEmptyString = Field(alias="from")
    router: NonEmptyString
    routes: dict[NonEmptyString, NonEmptyString] = Field(min_length=1)

    @field_validator("routes")
    @classmethod
    def validate_routes(cls, routes: dict[str, str]) -> dict[str, str]:
        if "START" in routes.values():
            raise ValueError("START cannot be a route destination")
        return routes


EdgeDefinition = DirectEdge | ConditionalEdge


class WorkflowDefinition(StrictDefinition):
    schema_version: Literal[1]
    name: NonEmptyString
    start: NonEmptyString
    nodes: dict[NodeId, NodeDefinition] = Field(min_length=1)
    edges: tuple[EdgeDefinition, ...] = Field(default_factory=tuple)

    @field_validator("nodes")
    @classmethod
    def validate_node_names(
        cls, nodes: dict[str, NodeDefinition]
    ) -> dict[str, NodeDefinition]:
        reserved = {"START", "END"}.intersection(nodes)
        if reserved:
            raise ValueError(f"Reserved node IDs are not allowed: {sorted(reserved)}")
        return nodes
