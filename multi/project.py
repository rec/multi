from pathlib import Path
import datacls


@datacls
class Project:
    name: str
    settings: dict
    path: Path
    argv: tuple

    @property
    def pyproject(self):
        return self.path / 'pyproject.toml'
