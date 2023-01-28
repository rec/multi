from pathlib import Path
from loady import importer
from typer import Argument, Option, Typer
import copy
import json
import sys

__all__ = 'app', 'command'

ROOT = Path(__file__).parents[1]
PROJECTS_FILE = ROOT / 'projects.json'
PROJECTS_BACK_FILE = PROJECTS_FILE.with_suffix('.json.bak')
PROJECTS_DATA = json.loads(PROJECTS_FILE.read_text())
PROJECTS_BACK = copy.deepcopy(PROJECTS_DATA)
_PROJECTS = []

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=f'')

command = app.command


@app.callback()
def main(
    projects: list[str] = Option(sorted(PROJECTS_DATA)),
):
    _PROJECTS[:] = projects


def _write_one(p, d):
    p.write_text(json.dumps(d, indent=4) + '\n')


def _write():
    _write_one(PROJECTS_FILE, PROJECTS_DATA)
    _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)


@command(name='list')
def _list():
    print(json.dumps(PROJECTS_DATA, indent=2))


@command()
def run(
    command: str = Argument(...),
):
    f = importer.import_code(command, base_path=ROOT)
    projects = {k: PROJECTS_DATA[k] for k in _PROJECTS}
    for k, v in sorted(projects.items()):
        f(k, v)


def test(*a, **ka):
    print('here!', a, ka)


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

        d = PROJECTS_DATA
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
