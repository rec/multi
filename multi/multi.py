from . import configs
from . projects import PROJECTS
from functools import wraps
from typer import Argument, Option, Typer
import importlib
import inspect
import sys
import time

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

command = app.command


@command()
def run(
    command: str = Argument(
        'name'
    ),

    argv: list[str] = Argument(
        None
    ),

    continue_after_error: bool = Option(
        False, '--continue-after-error', '-e'
    ),

    exclude: list[str] = Option(
        (), '--exclude', '-x'
    ),

    filter: list[str] = Option(
        None, '--filter', '-f'
    ),

    _open: bool = Option(
        configs.open, '--open', '-o'
    ),

    negated_filter: list[str] = Option(
        None, '--negated-filter', '-n'
    ),

    projects: list[str] = Option(
        tuple(PROJECTS), '--projects', '-p'
    ),

    push: bool = Option(
        False
    ),

    sort: bool = Option(
        False, '--sort', '-s',
    ),

    verbose: bool = Option(
        configs.verbose, '--verbose', '-v'
    ),
):
    configs.open = _open
    configs.push = push
    configs.verbose = verbose

    cmd_name, *configs.args = command.split(':')

    try:
        cmd = _get_callable('multi.commands.' + cmd_name)
    except Exception:
        # It's a get?
        cmd = _get_callable('multi.commands.get')
        argv.insert(0, command)
        configs.args = []

    filt = [_make_filter(f) for f in filter or ()]
    nfilt = [_make_filter(f) for f in negated_filter or ()]
    wait_at_end = False

    if not inspect.signature(cmd).parameters:
        wait_at_end = cmd()

    else:
        projects = [i for p in projects for i in p.split(':')]
        projects = [p for p in projects if p not in exclude]

        if sort:
            projects.sort()

        for name in projects:
            p = PROJECTS[name]
            try:
                if all(f(p) for f in filt) and not any(f(p) for f in nfilt):
                    if cmd(p, *argv):
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


def _get_one_callable(name, path, attr):
    module = importlib.import_module(path)
    none = object()

    if callable(f := getattr(module, attr, none)):
        return f
    if f is none:
        msg = ValueError(f'ERROR: {name} does not exist ({module=}, {f=})')
    else:
        msg = f'ERROR: {name} is not callable ({module=}, {f=})'
    raise ValueError(msg)


def _get_callable(name):
    path, _, attr = name.rpartition('.')

    try:
        return _get_one_callable(name, path, attr)
    except ValueError:
        pass
    return _get_one_callable(name, f'{path}.{attr}', attr)


def _make_filter(filter):
    first, *args = filter.split(':')
    filt = _get_callable('multi.filters.' + (first or tag))

    @wraps(filt)
    def wrapped(project):
        return bool(filt(project, *args))

    return wrapped


if __name__ == '__main__':
    app(standalone_mode=False)
