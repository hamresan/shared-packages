"""Exercise the real LangGraph Sellora demo from its documented script path."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_example() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "examples" / "sellora_mock.py"
    spec = importlib.util.spec_from_file_location("sellora_mock", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import example: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cart_quantities_and_full_trace() -> None:
    demo = load_example()
    result = demo.run_demo(["sku-1", "sku-1", "sku-2"])
    assert result["cart"] == {"sku-1": 2, "sku-2": 1}
    assert result["status"] == "tracked_mock"
    assert result["tracking_id"] == "DEMO-0001"
    assert result["cursor"] == 3
    assert result["trace"] == [
        "search:sku-1",
        "cart:sku-1",
        "search:sku-1",
        "cart:sku-1",
        "search:sku-2",
        "cart:sku-2",
        "search:done",
        "checkout",
        "review",
        "payment:mock",
        "tracking",
    ]


def test_empty_selection_finishes_with_empty_cart() -> None:
    result = load_example().run_demo([])
    assert result["cart"] == {}
    assert result["trace"] == [
        "search:done",
        "checkout",
        "review",
        "payment:mock",
        "tracking",
    ]


def test_unknown_sku_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown catalog SKU: unknown"):
        load_example().run_demo(["unknown"])


def test_runs_are_independent_and_repeatable() -> None:
    demo = load_example()
    first = demo.run_demo(["sku-1"])
    second = demo.run_demo(["sku-1"])
    assert first == second
    assert first["cart"] == {"sku-1": 1}


def test_documented_example_files_exist() -> None:
    path = Path(__file__).resolve().parents[2] / "examples" / "sellora_mock.py"
    assert path.is_file()
    assert path.with_name("sellora_workflow.yaml").is_file()
