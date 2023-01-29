from . project import Project
from pathlib import Path
from loady.importer import import_code
from typer import Argument, Option, Typer
import copy
import json
import sys

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


@command()
def run(
    command: str = Argument('name'),
    filter: str = Option(None, '--filter', '-f'),
    negate: bool = Option(False, '--negate', '-n'),
    projects: list[str] = Option(
        sorted(PROJECTS_DATA),
        '--projects', '-p'
    ),
):
    command = import_code('multi.commands.' + command)
    if filter:
        filter = import_code('multi.filters.' + filter)
        if negate:
            filter = _negate(filter)
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
            print('ERROR', e, file=sys.stderr)
            success = False

    sys.exit(not success)


def _negate(f):
    def wrapped(*a, **ka):
        return not f(*a, **ka)
    return wrapped


def _write_one(p, d):
    p.write_text(json.dumps(d, indent=4) + '\n')


def _write():
    if PROJECTS_BACK:
        _write_one(PROJECTS_BACK_FILE, PROJECTS_BACK)
        PROJECTS_BACK.clear()

    _write_one(PROJECTS_FILE, PROJECTS_DATA)


if __name__ == '__main__':
    app(standalone_mode=False)
