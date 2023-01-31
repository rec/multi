from functools import cached_property
from pathlib import Path
import datacls
import json
import sys
import tomlkit
import subprocess
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

    @cached_property
    def poetry_data(self):
        return self.pyproject.setdefault('tool', {}).setdefault('poetry', {})

    def read(self, *files):
        for file in files:
            if (f := self.path / file).exists():
                with f.open() as fp:
                    yield from fp

    @cached_property
    def readme(self):
        if r := self.poetry_data.get('readme', None):
            return r

        for r in 'README.md', 'README.rst':
            if (self.path / r).exists():
                return r

        return '?'

    @cached_property
    def python_path(self):
        return max(self.path.glob('.direnv/python-3.*.*/bin/python'))

    def branch(self):
        return self.run_out('git rev-parse --abbrev-ref HEAD').strip()

    @cached_property
    def url(self):
        return f'https://github.com/rec/{self.name}'

    def open_url(self, *parts):
        webbrowser.open('/'.join((self.url, *parts)))

    def run_out(self, *args, **kwargs):
        """Run and return stdout as a string on success, else ''"""
        kwargs.setdefault('out', True)
        return self.run(*args, **kwargs)

    def run(self, *args, out=False, **kwargs):
        if out:
            kwargs.setdefault('stdout', subprocess.PIPE)

        kwargs.setdefault('check', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('cwd', self.path)

        if len(args) == 1 and isinstance(args[0], str):
            args = args[0].split()

        r = subprocess.run(args, **kwargs)
        if not out:
            return r
        elif r:
            return r.stdout
        else:
            return ''

    def run_in(self, *args, **kwargs):
        return self.run(RUN_SH, *args, **kwargs)

    def run_arm(self, *args, **kwargs):
        return self.run_in('arch', '-arm64', *args, **kwargs)

    def poetry(self, *args, out=False, **kwargs):
        return self.run_arm('poetry', '--no-ansi', *args, **kwargs)

    def commit(self, msg, *files):
        files = [str(i) for i in files]
        self.run('git', 'add', *files)
        self.run('git', 'commit', '-m', msg, *files)
        self.run('git', 'push')

    @cached_property
    def is_singleton(self):
        return (self.path / self.name).with_suffix('.py').exists()
