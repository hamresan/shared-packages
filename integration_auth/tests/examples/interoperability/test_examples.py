"""Executable interoperability example tests."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).parents[3]
EXAMPLES = PACKAGE_ROOT / "examples" / "interoperability"


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PACKAGE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_python_protocol_known_answer_vectors() -> None:
    result = run_command([sys.executable, str(EXAMPLES / "python_protocol.py")])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == '{"inbound": true, "outbound": true}'


def test_python_rotation_and_authorization_example() -> None:
    result = run_command([sys.executable, str(EXAMPLES / "python_lifecycle_authorization.py")])

    assert result.returncode == 0, result.stderr
    assert '"rotation_inbound_only": true' in result.stdout
    assert '"permission_allow": true' in result.stdout
    assert '"permission_deny": true' in result.stdout
    assert '"scope_allow": true' in result.stdout
    assert '"scope_deny": true' in result.stdout


def test_php_protocol_matches_same_known_answer_vectors() -> None:
    php = shutil.which("php")
    if php is None:
        pytest.skip("PHP CLI is not installed")

    result = run_command([php, str(EXAMPLES / "php_protocol.php")])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == '{"inbound":true,"outbound":true}'
