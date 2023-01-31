from functools import cached_property
from pathlib import Path
import datacls
import json
import sys
import tomlkit
import webbrowser

ROOT = Path(__file__).parents[1]
SCRIPTS = ROOT / 'scripts'
RUN_SH = str(SCRIPTS / 'run.sh')


@datacls(order=True)
class Project:
    name: str
    settings: dict = datacls.field(compare=False)
    path: Path

    @cached_property
    def pyproject_file(self):
        return self.path / 'pyproject.toml'

    @cached_property
    def pyproject(self):
        return tomlkit.loads(self.pyproject_file.read_text())

    def write(self):
        self.pyproject_file.write_text(tomlkit.dumps(self.pyproject))

    @cached_property
    def poetry(self):
        return self.pyproject.setdefault('tool', {}).setdefault('poetry', {})

    @cached_property
    def multi(self):
        return self.pyproject.setdefault('tool', {}).setdefault('multi', {})

    @cached_property
    def run(self):
        from . runner import Runner

        return Runner(self.path)

    @cached_property
    def bin_path(self):
        return max(self.path.glob('.direnv/python-3.*.*/bin'))

    def branch(self):
        return self.run_out('git rev-parse --abbrev-ref HEAD').strip()

    @cached_property
    def url(self):
        return f'https://github.com/rec/{self.name}'

    def open_url(self, *parts):
        webbrowser.open('/'.join((self.url, *parts)))

    @cached_property
    def is_singleton(self):
        return (self.path / self.name).with_suffix('.py').exists()
