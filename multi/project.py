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

_VERSIONS = {
    'bbcprc': '0.1.0',
    'blocks': '1.0.0',
    'vl8': '0.2.0',
}

_DESCS = {
    'bbcprc': '🎙 The voice of Beeb 🎙',
    'blocks': '⬜🟩🟦🟥 Solve a block puzzle I found in Utrecht Lunetten 🟥🟦🟩⬜',
    'cfgs': '🍇 Implements the XDG standard for persistent files 🍇',
    'hardback': 'Hardcopy backups of digital data',
    'loady': 'Load Python libraries, JSON and raw text dynamically from git',
}

_ALL_PROPS = [
    'description',
    'python_version',
    'readme',
    'version',
]


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
    def poetry(self):
        return self.pyproject.get('tool', {}).get('poetry', {})

    @cached_property
    def python_version(self):
        return self.dependencies.get('python', '^3.7')

    @cached_property
    def dependencies(self):
        return self.poetry.get('dependencies', {})

    @cached_property
    def description(self):
        if r := _DESCS.get(self.name):
            return r
        if r := self.poetry.get('description', None):
            return r

        parts = [i.partition('=') for i in self.read('setup.py')]
        descs = (v for k, _, v in parts if k.strip() == 'description')
        return next(descs, '?').strip().strip(',').strip("'")

    def read(self, *files):
        for file in files:
            if (f := self.path / file).exists():
                with f.open() as fp:
                    yield from fp

    @cached_property
    def readme(self):
        if r := self.poetry.get('readme', None):
            return r

        for r in 'README.md', 'README.rst':
            if (self.path / r).exists():
                return r

        return '?'

    @cached_property
    def version(self):
        if self.poetry:
            return self.poetry['version']

        if v := _VERSIONS.get(self.name):
            return v

        for path in self.path.rglob('VERSION'):
            return path.read_text().strip()

        for line in self.read(*self.path.rglob('*.py')):
            e, _, version = line.strip().partition('__version__ = ')
            version = version.strip("'")
            if version and version != 'unknown' and not e:
                return version

        if self.name == 'vl8':
            return '0.2.0'

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

    @cached_property
    def all(self):
        return {k: getattr(self, k) for k in _ALL_PROPS}

    def run_out(self, *args, **kwargs):
        """Run and return stdout as a string on success, else ''"""
        kwargs.setdefault('stdout', subprocess.PIPE)
        if r := self.run(*args, **kwargs):
            return r.stdout
        return ''

    def run(self, *args, **kwargs):
        kwargs.setdefault('check', True)
        kwargs.setdefault('text', True)
        kwargs.setdefault('cwd', self.path)

        if len(args) == 1 and isinstance(args[0], str):
            args = args[0].split()

        return subprocess.run(args, **kwargs)

    def run_in(self, *args, out=False, **kwargs):
        method = self.run_out if out else self.run
        return method(RUN_SH, *args, **kwargs)

    def poet(self, *args, out=False, **kwargs):
        return self.run_in(
            'arch', '-arm64', 'poetry', '--no-ansi', *args, **kwargs
        )
