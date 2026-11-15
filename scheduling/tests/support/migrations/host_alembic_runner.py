"""Generate and apply a real disposable consumer migration revision."""

from pathlib import Path
from shutil import copyfile

from alembic import command
from alembic.config import Config


class HostAlembicRunner:
    """Host-owned migration lifecycle, exercised against SQLite or PostgreSQL."""

    def __init__(self, work_directory: Path, database_url: str) -> None:
        self._script_directory = work_directory / "alembic"
        self._database_url = database_url
        self._config: Config | None = None

    def create_and_upgrade(self) -> Path:
        config = Config(str(self._script_directory.parent / "alembic.ini"))
        config.set_main_option("script_location", str(self._script_directory))
        config.set_main_option("sqlalchemy.url", self._database_url)
        command.init(config, str(self._script_directory), template="async")
        config.set_main_option("sqlalchemy.url", self._database_url)
        copyfile(Path(__file__).with_name("host_env.py"), self._script_directory / "env.py")
        script = command.revision(config, message="host scheduling baseline", autogenerate=True)
        if script is None or isinstance(script, list):
            raise RuntimeError("Expected exactly one generated consumer Alembic revision.")
        command.upgrade(config, "head")
        self._config = config
        return Path(script.path)

    def downgrade(self) -> None:
        if self._config is None:
            raise RuntimeError("Migrations have not been initialized.")
        command.downgrade(self._config, "base")
