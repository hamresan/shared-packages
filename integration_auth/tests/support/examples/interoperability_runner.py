"""Subprocess runner for executable interoperability examples."""

from __future__ import annotations

import subprocess
from pathlib import Path


class InteroperabilityExampleRunner:
    """Run one example command from the integration-auth package root."""

    def __init__(self, package_root: Path) -> None:
        self._package_root = package_root

    def run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self._package_root,
            check=False,
            capture_output=True,
            text=True,
        )
