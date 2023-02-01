from . project import Project
from pathlib import Path
from typer import Argument, Option, Typer
import copy
import json
import sys
import time

_NAMES = [
    'abbrev', 'backer', 'blocks', 'cfgs',
    'datacls', 'def_main', 'dek', 'dtyper',

    'editor', 'gitz', 'hardback', 'impall',
    'loady', 'multi', 'nc', 'nmr',

    'plur', 'runs', 'safer', 'sproc',
    'tdir', 'vl8', 'wavemap', 'xmod',
]


PROJECTS = {k: Project(k, i) for i, k in enumerate(_NAMES)}
MULTI = PROJECTS['multi']

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

command = app.command


@command()
def run(
    command: str = Argument('name'),
    argv: list[str] = Argument(None),
    commit: str = Option('', '--commit', '-c'),
    continue_after_error: bool = Option(True, '--continue-after-error', '-e'),
    filter: str = Option(None, '--filter', '-f'),
    negate: bool = Option(False, '--negate', '-n'),
    projects: list[str] = Option(sorted(PROJECTS), '--projects', '-p'),
):
    from multi import commands, filters

    cmd = _get_callable(commands, command)

    if not filter:
        filt = lambda *_: True
    else:
        filt = _get_callable(filters, filter)
        if negate:
            filt = _negate(filt)

    wait_at_end = False

    for project in sorted(PROJECTS[k] for k in projects):
        try:
            if filt(project):
                wait_at_end = cmd(project, *argv) or wait_at_end

            if commit:
                pass

        except Exception as e:
            if not continue_after_error:
                raise
            print('ERROR', e, file=sys.stderr)
            fail = True

    if wait_at_end:
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Done')

    sys.exit('fail' in locals())


def _get_callable(o, name):
    if callable(f := getattr(o, name, None)):
        return f
    print(f'ERROR: {name} is not callable')
    sys.exit(-1)


def _negate(f):
    def wrapped(*a, **ka):
        return not f(*a, **ka)
    return wrapped


if __name__ == '__main__':
    app(standalone_mode=False)
