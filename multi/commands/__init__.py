from . get import get
from . data import assign
from . poetry import bump_version, run_poetry
from . run import run, bash
from . tags import add_tag, remove_tag

import sys

__all__ = (
    'add_tag',
    'assign',
    'bash',
    'bump_version',
    'get',
    'name',
    'remove_tag',
    'run',
    'run_poetry',
)


def name(project):
    print(project.site_name)


def _exit(*args):
    # Elsewhere.
    if args:
        print(*args, file=sys.stderr)
        exit(-1)
    exit(0)
