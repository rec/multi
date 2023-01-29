from functools import cached_property
from pathlib import Path
import datacls
import json
import tomlkit

_VERSIONS = {
    'bbcprc': '0.1.0',
    'blocks': '1.0.0',
    'vl8': '0.2.0',
}


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

    @cached_property
    def python_version(self):
        if d := self.dependencies.get('python', None):
            return d
        return '?'

    @cached_property
    def dependencies(self):
        if self.is_poetry:
            return self.pyproject['tool']['poetry']['dependencies']
        return {}

    @cached_property
    def version(self):
        if self.is_poetry:
            return self.pyproject['tool']['poetry']['version']

        if v := _VERSIONS.get(self.name):
            return v

        for path in self.path.rglob('VERSION'):
            return path.read_text().strip()

        for path in self.path.rglob('*.py'):
            for line in path.read_text().splitlines():
                e, _, version = line.strip().partition('__version__ = ')
                version = version.strip("'")
                if version and version != 'unknown' and not e:
                    return version

        if self.name == 'vl8':
            return '0.2.0'

        return '?'
