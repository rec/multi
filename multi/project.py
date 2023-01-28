from functools import cached_property
from pathlib import Path
import datacls
import json
import tomlkit


@datacls
class Project:
    name: str
    settings: dict
    path: Path
    argv: tuple

    @cached_property
    def pyproject_file(self):
        return self.path / 'pyproject.toml'

    @cached_property
    def pyproject(self):
        if not self.pyproject_file.exists():
            return {}

        return tomlkit.loads(self.pyproject_file.read_text())

    @cached_property
    def is_poetry(self):
        return self.pyproject.get('tool', {}).get('poetry', {})
