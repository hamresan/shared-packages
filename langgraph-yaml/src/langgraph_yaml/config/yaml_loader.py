"""Safe YAML parsing with duplicate mapping key rejection."""

from typing import Protocol, cast

import yaml

from langgraph_yaml.config.errors import WorkflowLoadError


class YamlObjectConstructor(Protocol):
    """Typed boundary for PyYAML's incompletely annotated constructor."""

    def construct_object(self, node: yaml.Node, deep: bool = False) -> object: ...


class UniqueKeySafeLoader(yaml.SafeLoader):
    """SafeLoader that refuses duplicate keys in any mapping."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader,
    node: yaml.MappingNode,
) -> dict[object, object]:
    """Construct a mapping while preserving the location of duplicate keys."""
    loader.flatten_mapping(node)
    result: dict[object, object] = {}
    constructor = cast(YamlObjectConstructor, loader)
    for key_node, value_node in node.value:
        key = constructor.construct_object(key_node, deep=True)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        result[key] = constructor.construct_object(value_node, deep=True)
    return result


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def parse_yaml_mapping(text: str, *, source: str) -> dict[str, object]:
    """Parse safe YAML, rejecting duplicate keys and non-mapping documents."""
    try:
        data: object = yaml.load(text, Loader=UniqueKeySafeLoader)
    except yaml.YAMLError as exc:
        raise WorkflowLoadError(f"{source}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise WorkflowLoadError(f"{source}: expected a YAML mapping at document root")
    return cast(dict[str, object], data)
