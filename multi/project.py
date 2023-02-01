from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
import datacls
import json
import sys
import tomlkit
import webbrowser

CODE_ROOT = Path('/code')
SCRIPTS = Path(__file__).parents[1] / 'scripts'
RUN_SH = str(SCRIPTS / 'run.sh')


@datacls
class Opener:
    url: str

    def __call__(self, *parts, new=1, autoraise=True):
        webbrowser.open('/'.join((self.url, *parts)), 1)



@datacls(order=True)
class Project:
    name: str
    index: int

    @cached_property
    def path(self):
        return CODE_ROOT / self.name

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
    def multi(self):  # My data
        return self.pyproject.setdefault('tool', {}).setdefault('multi', {})

    @cached_property
    def git(self):
        from . git import Git

        return Git(self.run)

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
    def server_url(self):
        return f'127.0.0.1:{7000 + self.index}'

    @cached_property
    def git_url(self):
        return f'https://github.com/rec/{self.name}'

    @cached_property
    def open_git(self):
        return Opener(self.git_url)

    @cached_property
    def open_server(self):
        return Opener('http://' + self.server_url)

    @cached_property
    def is_singleton(self):
        return (self.path / self.name).with_suffix('.py').exists()
