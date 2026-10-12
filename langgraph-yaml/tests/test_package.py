"""Smoke tests for the package boundary."""

from importlib.metadata import version

import langgraph_yaml


def test_package_exposes_version() -> None:
    assert langgraph_yaml.__version__ == "0.1.0.dev0"


def test_distribution_metadata_is_available() -> None:
    assert version("langgraph-yaml") == langgraph_yaml.__version__
