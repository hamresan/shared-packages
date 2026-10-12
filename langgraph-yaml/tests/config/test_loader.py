"""Tests for safe YAML workflow loading."""

from pathlib import Path

import pytest

from langgraph_yaml.config.errors import WorkflowLoadError
from langgraph_yaml.config.loader import load_workflow, parse_workflow

VALID_YAML = """
schema_version: 1
name: example
start: first
nodes:
  first:
    handler: first_handler
  second:
    handler: second_handler
edges:
  - from: first
    to: second
  - from: second
    router: choice
    routes:
      again: first
      done: END
"""


def test_parse_valid_yaml() -> None:
    definition = parse_workflow(VALID_YAML)
    assert definition.name == "example"
    assert len(definition.edges) == 2


def test_load_file(tmp_path: Path) -> None:
    path = tmp_path / "workflow.yaml"
    path.write_text(VALID_YAML, encoding="utf-8")
    assert load_workflow(path).start == "first"


@pytest.mark.parametrize(
    "text",
    [
        VALID_YAML + "\nname: duplicate\n",
        VALID_YAML.replace("      done: END", "      again: END"),
        VALID_YAML.replace(
            "    handler: first_handler",
            "    handler: first_handler\n    handler: duplicate",
        ),
        VALID_YAML.replace(
            "  second:\n    handler: second_handler",
            "  first:\n    handler: second_handler",
        ),
    ],
)
def test_duplicate_keys_are_rejected(text: str) -> None:
    with pytest.raises(WorkflowLoadError, match="duplicate key") as exc:
        parse_workflow(text)
    assert "line" in str(exc.value)


@pytest.mark.parametrize("text", ["", "null", "[]", "- item", "42"])
def test_non_mapping_root_is_rejected(text: str) -> None:
    with pytest.raises(WorkflowLoadError, match="document root"):
        parse_workflow(text)


def test_malformed_yaml_is_rejected() -> None:
    with pytest.raises(WorkflowLoadError, match="invalid YAML"):
        parse_workflow("nodes: [broken")


def test_unsafe_python_tag_is_rejected() -> None:
    with pytest.raises(WorkflowLoadError, match="invalid YAML"):
        parse_workflow("!!python/object/apply:os.system ['echo unsafe']")


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(WorkflowLoadError, match="cannot read"):
        load_workflow(tmp_path / "missing.yaml")


def test_invalid_utf8_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_bytes(b"\xff\xfe")
    with pytest.raises(WorkflowLoadError, match="UTF-8"):
        load_workflow(path)


def test_unsupported_schema_version_has_context() -> None:
    with pytest.raises(WorkflowLoadError, match="schema_version"):
        parse_workflow(VALID_YAML.replace("schema_version: 1", "schema_version: 2"))


def test_invalid_schema_has_source_context() -> None:
    with pytest.raises(WorkflowLoadError, match="custom.yaml"):
        parse_workflow(
            VALID_YAML.replace("handler: first_handler", "handler: ''"),
            source="custom.yaml",
        )


def test_whitespace_and_unicode_are_supported() -> None:
    text = VALID_YAML.replace("name: example", "name: فروشگاه")
    assert parse_workflow(text).name == "فروشگاه"
