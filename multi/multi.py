import inspect
import sys
import time

from pathlib import Path

from typer import Argument, Option, Typer

from multi.get_callable import get_callable, make_filter
from . import configs
from .projects import PROJECTS

app = Typer(
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
)
command = app.command


@command()
def run(
    command: str = Argument('name'),
    argv: list[str] = Argument(None),
    all_: bool = Option(False, '--all', '-a'),
    continue_after_error: bool = Option(False, '--continue-after-error', '-e'),
    exclude: list[str] = Option((), '--exclude', '-x'),
    filter: list[str] = Option(None, '--filter', '-f'),
    _open: bool = Option(configs.open, '--open', '-o'),
    negated_filter: list[str] = Option(None, '--negated-filter', '-n'),
    projects: list[str] = Option((), '--projects', '-p'),
    push: bool = Option(False),
    sort: bool = Option(False, '--sort', '-S'),
    verbose: bool = Option(configs.verbose, '--verbose', '-v'),
):
    configs.open = _open
    configs.push = push
    configs.verbose = verbose

    cmd_name, *configs.args = command.split(':')
    try:
        cmd = get_callable('multi.commands.' + cmd_name)
    except ValueError:
        # It's a get?
        cmd = get_callable('multi.commands.get')
        argv.insert(0, command)
        configs.args = []

    filt = [make_filter(f) for f in filter or ()]
    nfilt = [make_filter(f) for f in negated_filter or ()]
    wait_at_end = False

    if not inspect.signature(cmd).parameters:
        wait_at_end = cmd()

    else:
        if projects:
            projects = [i for p in projects for i in p.split(':')]
        elif all_:
            projects = tuple(PROJECTS)
        else:
            cwd = Path().absolute()
            try:
                projects = [next(p.name for p in PROJECTS.values() if cwd.is_relative_to(p.path))]
            except StopIteration:
                sys.exit(f'{cwd} is not in a known project')
        projects = [p for p in projects if p not in exclude]

        if sort:
            projects.sort()

        for name in projects:
            p = PROJECTS[name]
            try:
                if all(f(p) for f in filt) and not any(f(p) for f in nfilt):
                    if verbose:
                        p.p(f'{cmd.__module__}.{cmd.__name__}')
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


if __name__ == '__main__':
    app(standalone_mode=False)
