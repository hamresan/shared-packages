"""Check wheel/sdist resources without importing optional providers."""

import tarfile
import zipfile
from pathlib import Path


def verify_distributions(dist: Path) -> None:
    wheels = sorted(dist.glob("hamresan_customer-*.whl"))
    sources = sorted(dist.glob("hamresan_customer-*.tar.gz"))
    if len(wheels) != 1 or len(sources) != 1:
        raise RuntimeError("Exactly one wheel and one source archive are required")

    with zipfile.ZipFile(wheels[0]) as archive:
        files = set(archive.namelist())
        required = {
            "customer/__init__.py",
            "customer/py.typed",
            "customer/migrations/alembic.py",
            "customer/migrations/rls.py",
            "customer/presentation/http/router.py",
        }
        if not required.issubset(files):
            raise RuntimeError(f"Missing wheel resources: {sorted(required - files)}")
        if any(name.startswith(("tests/", "examples/")) for name in files):
            raise RuntimeError("Development-only files leaked into the runtime wheel")

    with tarfile.open(sources[0], "r:gz") as archive:
        files = {name.split("/", 1)[1] for name in archive.getnames() if "/" in name}
        required = {
            "src/customer/py.typed",
            "src/customer/migrations/rls.py",
            "docs/HTTP_INTEGRATION.md",
            "docs/SECURITY_AND_ACCEPTANCE.md",
            "examples/guest_lifecycle.py",
            "examples/http_router.py",
            "README.md",
            "ROADMAP.md",
            "CHANGELOG.md",
            "pyproject.toml",
        }
        if not required.issubset(files):
            raise RuntimeError(f"Missing source resources: {sorted(required - files)}")


if __name__ == "__main__":
    verify_distributions(Path(__file__).resolve().parents[1] / "dist")
