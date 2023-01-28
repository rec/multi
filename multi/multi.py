from . project import Project
from pathlib import Path
from loady.importer import import_code
from typer import Argument, Option, Typer
import copy
import json
import sys

__all__ = 'app', 'command'

CODE_ROOT = Path('/code')

ROOT = Path(__file__).parents[1]
PROJECTS_FILE = ROOT / 'projects.json'
PROJECTS_BACK_FILE = PROJECTS_FILE.with_suffix('.json.bak')
PROJECTS_DATA = json.loads(PROJECTS_FILE.read_text())
PROJECTS_BACK = copy.deepcopy(PROJECTS_DATA)
MULTIPLE_COMMANDS = False

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=f'')

command = app.command


def _negate(f):
    def wrapped(*a, **ka):
        return not f(*a, **ka)
    return wrapped


@command()
def run(
    command: str = Argument('name'),
    filter: str = Option(None),
    negate: bool = Option(False),
    projects: list[str] = Option(sorted(PROJECTS_DATA)),
):
    command = import_code('multi.commands.' + command)
    if filter:
        filter = import_code('multi.filters.' + filter)
    else:
        filter = lambda p: True

    projects = {k: PROJECTS_DATA[k] for k in projects}
    success = True

    for k, v in sorted(projects.items()):
        project = Project(k, v, CODE_ROOT / k, ())
        try:
            if filter(project) and command(project):
                _write()
        except Exception as e:
            print(e)
            success = False

    sys.exit(not success)


def _write_one(p, d):
    p.write_text(json.dumps(d, indent=4) + '\n')


def _write():
    if PROJECTS_BACK:
        _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)
        PROJECTS_BACK.clear()

    _write_one(PROJECTS_FILE, PROJECTS_DATA)


if MULTIPLE_COMMANDS:
    @app.callback()
    def main(
        filter: str = Option(None),
        negate: bool = Option(False),
        projects: list[str] = Option(sorted(PROJECTS_DATA)),
    ):
        _PROJECTS[:] = projects
        if filter:
            code = import_code('multi.filters.' + filter)
        else:
            code = lambda *a, **ka: True

        if negate and filter:
            code = _negate(code)

        _FILTER[:] = [code]

    @command(name='list')
    def _list():
        print(json.dumps(PROJECTS_DATA, indent=2))

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
