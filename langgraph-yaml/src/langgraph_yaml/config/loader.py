"""Read YAML workflow definitions and validate them with Pydantic."""

from pathlib import Path

from pydantic import ValidationError

from langgraph_yaml.config.errors import WorkflowLoadError
from langgraph_yaml.config.models import WorkflowDefinition
from langgraph_yaml.config.yaml_loader import parse_yaml_mapping


def parse_workflow(text: str, *, source: str = "<string>") -> WorkflowDefinition:
    """Validate a YAML workflow without performing graph reference checks."""
    data = parse_yaml_mapping(text, source=source)
    try:
        return WorkflowDefinition.model_validate(data)
    except ValidationError as exc:
        raise WorkflowLoadError(f"{source}: invalid workflow definition: {exc}") from exc


def load_workflow(path: str | Path) -> WorkflowDefinition:
    """Read a UTF-8 YAML workflow file and validate its schema."""
    file_path = Path(path)
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise WorkflowLoadError(f"{file_path}: cannot read UTF-8 YAML file: {exc}") from exc
    return parse_workflow(text, source=str(file_path))
