"""Installed-package-facing public API smoke expectations."""

import importlib


def test_supported_public_packages_import_without_optional_frameworks() -> None:
    modules = (
        "instagram_api",
        "instagram_api.application.accounts",
        "instagram_api.application.comments",
        "instagram_api.application.contracts",
        "instagram_api.application.media",
        "instagram_api.application.messaging",
        "instagram_api.application.webhooks",
        "instagram_api.domain",
    )

    for module in modules:
        assert importlib.import_module(module) is not None
