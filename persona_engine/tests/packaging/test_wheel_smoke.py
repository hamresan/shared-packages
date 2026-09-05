import subprocess
import sys
import zipfile
from pathlib import Path


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

    wheel = next(output_dir.glob("hamresan_persona_engine-*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    assert "persona_engine/__init__.py" in names
    assert any(name.endswith(".dist-info/METADATA") for name in names)
