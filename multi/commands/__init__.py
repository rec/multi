from . files import clean_dir, cat, glob
from . get import get
from . git import fix_gitignore, tweak_github
from . mkdocs import add_mkdocs, serve
from . readme import open_readme, readme
from . tags import add_tag, remove_tag

from .. paths import PYPROJECT
import sys

__all__ = (
    'add_mkdocs',
    'add_tag',
    'cat',
    'clean_dir',
    'fix_gitignore',
    'get',
    'glob',
    'open_readme',
    'readme',
    'remove_tag',
    'serve',
    'tweak_github',
)


def bump_version(project, rule_or_version, *notes):
    project.run.poetry('version', rule_or_version)
    project.reload()

    version = 'v' + project.poetry['version']
    project.git.commit(f'Update to version {version}', PYPROJECT)
    project.git('tag', version)
    project.git('push', '--tag', '--force-with-lease')
    notes = ' '.join(notes).strip() or f'Version {version}'
    project.run.gh('release', 'create', '--notes', notes)


def assign(project, *argv):
    parts = [(k, v) for a in argv for k, _, v in a.partition('=')]
    if bad := sorted(a for a, (k, v) in zip(argv, parts) if not (k and v)):
        raise ValueError(f'No assignments in {bad}')

    with project.writer() as multi:
        for k, v in parts:
            *rest, last = k.split('.')
            m = multi
            for i in rest:
                m = m.setdefault(i, {})
            m[last] = v


def run(project, *argv):
    project.p()
    project.run(*argv)
    print()


def bash(project, *argv):
    project.p()
    project.run.bash(*argv)
    print()


def run_poetry(project, *argv):
    print(project.name + ':')
    project.run.poetry(*argv)
    print()


def name(project):
    print(project.site_name)


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)
