from . files import clean_dir, cat, glob
from . get import get
from . git import fix_gitignore, tweak_github
from . data import assign
from . mkdocs import add_mkdocs, serve
from . poetry import bump_version, run_poetry
from . readme import open_readme, readme
from . run import run, bash
from . tags import add_tag, remove_tag

import sys

__all__ = (
    'add_mkdocs',
    'add_tag',
    'assign',
    'bash',
    'bump_version',
    'cat',
    'clean_dir',
    'fix_gitignore',
    'get',
    'glob',
    'name',
    'open_readme',
    'readme',
    'remove_tag',
    'run',
    'run_poetry',
    'serve',
    'tweak_github',
)


def name(project):
    print(project.site_name)


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)
