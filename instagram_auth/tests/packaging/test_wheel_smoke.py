"""Smoke-test the built Instagram auth wheel artifact."""

import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile


def test_wheel_build_contains_public_package_and_metadata(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "dist"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(output_dir),
            str(project_root),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    wheels = tuple(output_dir.glob("hamresan_instagram_auth-*.whl"))
    assert len(wheels) == 1

    with ZipFile(wheels[0]) as wheel:
        names = frozenset(wheel.namelist())
        assert "instagram_auth/__init__.py" in names

        metadata_name = next(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = wheel.read(metadata_name).decode("utf-8")

    assert "Name: hamresan-instagram-auth" in metadata
    assert "Requires-Python: >=3.12" in metadata
    assert "Requires-Dist: fastapi" not in metadata
