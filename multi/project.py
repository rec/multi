from . import ROOT, SCRIPTS
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
import datacls
import json
import tomlkit
import webbrowser
import xmod

CODE_ROOT = Path('~/code').expanduser()
RUN_SH = str(SCRIPTS / 'run.sh')
FILE = ROOT / 'multi.toml'
DATA = tomlkit.loads(FILE.read_text())
BACK_FILE = FILE.with_suffix('.bak.toml')


@datacls
class Opener:
    url: str

    def __call__(self, *parts, new=1, autoraise=True):
        url = '/'.join((self.url, *parts))
        webbrowser.open(url, 1)
        return url


@datacls(order=True)
class Project:
    name: str
    tag: str
    rank: int = -1  # -1 means unranked

    RELOAD = 'description_parts', 'multi', 'pyproject_file', 'configs'

    def reload(self):
        for r in self.RELOAD:
            if r in self.__dict__:
                del self.__dict__[r]

    @cached_property
    def path(self) -> Path:
        return CODE_ROOT / self.name

    def make_path(self, *path):
        return self.path.make_path(*path)

    def read_lines(self, *path):
        return self.make_path(*path).read_text().splitlines()

    @cached_property
    def pyproject_file(self):
        from . paths import PYPROJECT
        return self.path / PYPROJECT

    @cached_property
    def user(self):
        return 'timedata-org' if self.name == 'loady' else 'rec'

    @cached_property
    def configs(self):
        try:
            return tomlkit.loads(self.pyproject_file.read_text())
        except FileNotFoundError:
            return {}

    @contextmanager
    def pyproject_writer(self):
        yield self.configs
        self.write_pyproject()

    def write_pyproject(self):
        self.pyproject_file.write_text(tomlkit.dumps(self.configs))

    def commit_pyproject(self, msg, *files):
        from . paths import PYPROJECT

        self.write_pyproject()
        self.git.commit(msg, PYPROJECT, *files)

    @cached_property
    def manager(self) -> dict:
        return self.configs.get('project') or self.poetry

    @cached_property
    def poetry(self) -> dict:
        return self.configs.get('tool', {}).get('poetry', {})

    @cached_property
    def package_manager(self) -> dict | None:
        return 'uv' if 'project' in self.configs else 'poetry' if self.poetry else ''

    @cached_property
    def version(self) -> str:
        return self.manager.get('version', '')

    @cached_property
    def tags(self) -> tuple[str, ...]:
        # wrong
        return tuple(sorted(k for k, v in DATA['tags'].items() if self.name in v))

    @cached_property
    def git(self):
        from . git import Git

        return Git(self.run)

    @cached_property
    def run(self):
        from . runner import Runner

        return Runner(self.path)

    @cached_property
    def bin_path(self) -> Path:
        if p := list(self.path.glob('.direnv/python-3.*/bin')):
            return max(p)
        if (p := Path('.venv/bin')).exists():
            return p
        raise ValueError(f'No binary path found in {self.path=}, {VENV_PATHS=}')

    def bin(self, *parts):
        return self.bin_path / ('/'.join(parts))

    def branch(self):
        return self.run.out('git', 'rev-parse', '--abbrev-ref', 'HEAD').strip()

    def branches(self, *a, **ka):
        lines = self.run.out('git', 'branch', *a, **ka).splitlines()
        return [i.split()[-1] for i in lines]

    def commit_id(self):
        return self.run.out('git', 'rev-parse', 'HEAD').strip()

    @cached_property
    def server_url(self):
        return f'127.0.0.1:{7000 + self.rank}'

    @cached_property
    def git_ssh_url(self):
        return f'git@github.com:{self.user}/{self.name}.git'

    @cached_property
    def git_url(self):
        return f'https://github.com/{self.user}/{self.name}'

    @cached_property
    def doc_url(self):
        return f'https://{self.user}.github.io/{self.name}'

    @cached_property
    def open_doc(self):
        if self.has_gh_pages():
            return Opener(self.doc_url)
        return lambda *a, **k: self.p('Has no gh_pages')

    @cached_property
    def open_gh(self):
        if self.has_gh_pages():
            return Opener(f'file://{self.gh_pages}/index.html')
        return lambda *a, **k: None

    @cached_property
    def has_gh_pages(self):
        br = [b.split('/')[-1].strip() for b in self.branches('-r')]
        return 'gh-pages' in br

    @cached_property
    def open_git(self):
        return Opener(self.git_url)

    @cached_property
    def open_server(self):
        return Opener('http://' + self.server_url)

    @cached_property
    def is_singleton(self):
        return (self.path / self.name).with_suffix('.py').exists()

    @cached_property
    def description(self):
        return self.manager.get('description') or DESCRIPTIONS.get(self.name, self.name)

    @cached_property
    def description_parts(self):
        d = self.description
        items = list(enumerate(d))

        begin = next(i for i, c in items if c.isascii())
        end = next(i for i, c in reversed(items) if c.isascii())

        if end == len(d) - 1:
            end = len(d)

        return d[:begin].strip(), d[begin:end].strip(), d[end:].strip()

    @cached_property
    def color(self):
        from . import projects

        return projects.color(self.rank)

    @cached_property
    def git_tag(self):
        tags = [i.strip() for i in self.run.out('git', 'tag').splitlines()]
        tags = [i[1:] for i in tags if i.startswith('v')]
        tags = [i.strip('.') for i in tags]
        tags = [[int(j) for j in i.split('.')] for i in tags]
        if tags:
            v0, v1, v2 = max(tags)
            return f'v{v0}.{v1}.{v2}'

    @cached_property
    def site_name(self):
        e1, desc, e2 = self.description_parts
        return f'{e1}: `{self.name}`: {desc} {e2}'

    def p(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], str):
            args = [args[0].rstrip()]

        print(f'{self.name:10}: ', *args, **kwargs)

    def python(self, *args, **kwargs):
        return self.run(str(self.bin('python')), *args, arm=True, **kwargs)

    @cached_property
    def python_version(self) -> str:
        m = self.manager
        return m.get('requires-python') or m.get('dependencies', {}).get('python') or ''

    @cached_property
    def comment(self):
        n = self.name
        a = xmod.WRAPPED_ATTRIBUTE
        cmd = f'import {n}; {n} = getattr({n}, "{a}", {n}); print({n}.__doc__)'
        lines = self.python('-c', cmd, out=True).strip().splitlines()

        emoji = self.description_parts[0]
        while lines and lines[0].startswith(emoji):
            lines.pop(0)
        while lines and not lines[0]:
            lines.pop(0)
        lines.append('')
        return '\n'.join(lines)

    @cached_property
    def gh_pages(self):
        cache = self.path / '.cache'
        path = cache / 'gh-pages'

        if self.has_gh_pages():
            if path.exists():
                if False:
                    self.git('pull', cwd=path)
            else:
                cache.mkdir(exist_ok=True, parents=True)
                self.git('clone', '-b', 'gh-pages', self.git_ssh_url, path)

        return path

    @cached_property
    def api_anchor(self):
        return f'{self.name}--api-documentation'

    def get_value(self, key, default=None):
        return DATA.get(key, {}).get(self.name, default)

    def set_value(self, key, value):
        from . import projects

        DATA.setdefault(key, {})[self.name] = value
        projects.write()

    @property
    def api_name(self):
        return self.get_value('api_path', self.name)

    @property
    def api_section(self):
        paths = self.get_value('api_paths', [self.api_name])
        return '\n\n'.join(f'::: {p}' for p in paths)

    @cached_property
    def github_api_url(self):
        return f'https://api.github.com/repos/{self.user}/{self.name}'

    def gh(self, *cmd):
        return json.loads(self.run('gh', 'api', *cmd, out=True))

    @cached_property
    def github_info(self):
        return self.gh('repos/{owner}/{repo}', '--cache', '3600s')


def _get(*keys):
    d = DATA
    for k in keys:
        d = d.setdefault(k, {})
    return d


DESCRIPTIONS = {
    'dotfiles': '⚫ My dotfiles ⚫',
    'test': '❓ Tiny bits of experimental code ❓',
}
