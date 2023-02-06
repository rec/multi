from . import configs
from . projects import PROJECTS
from functools import wraps
from typer import Argument, Option, Typer
import sys
import time

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
    filter: list[str] = Option(None, '--filter', '-f'),
    negate: bool = Option(False, '--negate', '-n'),
    projects: list[str] = Option(sorted(PROJECTS), '--projects', '-p'),
    verbose: bool = Option(configs.verbose, '--verbose', '-v'),
):
    from multi import commands

    configs.verbose = verbose

    cmd = _get_callable(commands, command)
    filt = _make_filters(filter, negate)
    wait_at_end = False

    projects = [i for p in projects for i in p.split(':')]
    projects = [p for p in projects if p not in exclude]

    for name in projects:
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
    none = object()
    if callable(f := getattr(o, name, none)):
        return f
    if f is none:
        msg = f'ERROR: {name} does not exist ({o=}, {f=})'
    else:
        msg = f'ERROR: {name} is not callable ({o=}, {f=})'
    if True:
        raise ValueError(msg)
    print(msg)
    sys.exit(-1)


def _make_filters(filters, negate):
    filters = [_make_filter(f, negate) for f in filters]

    def filter(project):
        return all(f(project) for f in filters)

    return filter


def _make_filter(filter, negate):
    from multi import filters

    if not filter:
        return lambda *_: True

    first, *args = filter.split(':')
    filt = _get_callable(filters, first)

    @wraps(filt)
    def wrapped(project):
        return bool(filt(project, *args)) != bool(negate)

    return wrapped


if __name__ == '__main__':
    app(standalone_mode=False)
