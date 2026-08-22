"""Install the built wheel in an isolated environment and smoke-test the public API."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def main() -> None:
    package_root = Path(__file__).resolve().parents[2]
    wheels = sorted((package_root / "dist").glob("hamresan_integration_auth-*.whl"))
    if len(wheels) != 1:
        raise SystemExit(f"expected exactly one built wheel, found {len(wheels)}")

    with tempfile.TemporaryDirectory(prefix="integration-auth-wheel-") as directory:
        environment = Path(directory) / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        subprocess.run(
            [str(python), "-m", "pip", "install", "--no-deps", str(wheels[0])],
            check=True,
        )
        subprocess.run(
            [
                str(python),
                "-c",
                (
                    "from integration_auth import IntegrationClientId, Permission; "
                    "assert IntegrationClientId('release-client').value == 'release-client'; "
                    "assert Permission('catalog.read').value == 'catalog.read'"
                ),
            ],
            check=True,
        )


if __name__ == "__main__":
    main()
