from . project import Project
from functools import wraps
from typer import Argument, Option, Typer
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
    continue_after_error: bool = Option(False, '--continue-after-error', '-e'),
    exclude: list[str] = Option((), '--exclude', '-e'),
    filter: str = Option(None, '--filter', '-f'),
    negate: bool = Option(False, '--negate', '-n'),
    projects: list[str] = Option(sorted(PROJECTS), '--projects', '-p'),
):
    from multi import commands

    cmd = _get_callable(commands, command)
    filt = _make_filter(filter, negate)
    wait_at_end = False

    for name in (p for p in projects if p not in exclude):
        project = PROJECTS[name]
        try:
            if filt(project) and cmd(project, *argv):
                wait_at_end = True

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


def _make_filter(filter, negate):
    from multi import filters

    if not filter:
        return lambda *_: True

    filt = _get_callable(filters, filter)
    if not negate:
        return filt

    @wraps(filt)
    def wrapped(*a, **ka):
        return not filt(*a, **ka)

    return wrapped


if __name__ == '__main__':
    app(standalone_mode=False)
