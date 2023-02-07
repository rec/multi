from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
import datacls
import tomlkit
import webbrowser
import xmod

CODE_ROOT = Path('/code')
SCRIPTS = Path(__file__).parents[1] / 'scripts'
CACHE = Path(__file__).parents[1] / '.cache'
GH_PAGE = CACHE / 'gh-page'
RUN_SH = str(SCRIPTS / 'run.sh')


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
    index: int

    RELOAD = 'description_parts', 'multi', 'poetry', 'pyproject_file'

    def reload(self):
        for r in self.RELOAD:
            if r in self.__dict__:
                del self.__dict__[r]

    @cached_property
    def path(self):
        return CODE_ROOT / self.name

    @cached_property
    def pyproject_file(self):
        return self.path / 'pyproject.toml'

    @cached_property
    def user(self):
        return 'timedata-org' if self.name == 'loady' else 'rec'

    @cached_property
    def pyproject(self):
        return tomlkit.loads(self.pyproject_file.read_text())

    @contextmanager
    def writer(self):
        yield self.pyproject
        self.write()

    def write(self):
        self.pyproject_file.write_text(tomlkit.dumps(self.pyproject))

    @cached_property
    def poetry(self):
        return self.pyproject.setdefault('tool', {}).setdefault('poetry', {})

    @cached_property
    def multi(self):
        return self.pyproject.setdefault('tool', {}).setdefault('multi', {})

    @cached_property
    def tags(self):
        return self.multi.setdefault('multi', [])

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

    def bin(self, *parts):
        return self.bin_path / ('/'.join(parts))

    def branch(self):
        return self.run.out('git', 'rev-parse', '--abbrev-ref', 'HEAD').strip()

    def branches(self):
        lines = self.run.out('git', 'branch').splitlines()
        return [i.split()[-1] for i in lines]

    def commit_id(self):
        return self.run.out('git', 'rev-parse', 'HEAD').strip()

    @cached_property
    def server_url(self):
        return f'127.0.0.1:{7000 + self.index}'

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
        return Opener(self.doc_url)

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
    def description_parts(self):
        d = self.poetry['description']
        items = list(enumerate(d))

        begin = next(i for i, c in items if c.isascii())
        end = next(i for i, c in reversed(items) if c.isascii())

        if end == len(d) - 1:
            end = len(d)

        return d[:begin].strip(), d[begin:end].strip(), d[end:].strip()

    @cached_property
    def color(self):
        from . import projects

        return projects.color(self.name)

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
        arm = not self.poetry['dependencies']['python'].endswith('3.7')
        return self.run(self.bin('python'), *args, arm=arm, **kwargs)

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

        if 'gh-pages' in self.branches():
            if path.exists():
                self.git('pull', cwd=path)
            else:
                cache.mkdir(exist_ok=True, parents=True)
                self.git('clone', '-b', 'gh-pages', self.git_ssh_url, path)

        return path
