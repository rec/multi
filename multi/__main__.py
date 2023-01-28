from pathlib import Path
from typer import Argument, Option, Typer
import copy
import json
import sys

__all__ = 'app', 'command'

PROJECTS_FILE = Path(__file__).parents[1] / 'projects.json'
PROJECTS_BACK_FILE = PROJECTS_FILE.with_suffix('.json.bak')
PROJECTS = json.loads(PROJECTS_FILE.read_text())
PROJECTS_BACK = copy.deepcopy(PROJECTS)

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=f'')

command = app.command


def _write_one(p, d):
    p.write_text(json.dumps(d, indent=4) + '\n')


def _write():
    _write_one(PROJECTS_FILE, PROJECTS)
    _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)


@command(name='list')
def _list():
    print(json.dumps(PROJECTS, indent=2))


@command(name='set')
def _set(
    arguments: list[str] = Argument(...),
):
    def arg(a):
        name, *value = (i.strip() for i in a.split('=', maxsplit=1))
        if not value:
            return

        *first, last = name.split('.')
        if not first:
            return

        d = PROJECTS
        for k in first:
            d = d.setdefault(k, {})

        return d, last, value

    args = [(a, arg(a)) for a in arguments]
    if missing := [k for k, v in args if not v]:
        print(f'{missing = }', file=sys.stderr)
        sys.exit(-1)

    for a, (d, last, value) in args:
        d[last] = value
        print('Set', a)

    _write()


if __name__ == '__main__':
    app(standalone_mode=False)
